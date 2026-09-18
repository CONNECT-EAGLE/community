"""Strict, bounded YAML loading and the bundled JSON Schema contract."""

from __future__ import annotations

import json
from importlib.resources import files
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

import yaml
from jsonschema import Draft202012Validator
from yaml.events import AliasEvent

from .repository import EagleError

MAX_BYTES = 64 * 1024


class UniqueLoader(yaml.SafeLoader):
    def compose_node(self, parent: Any, index: Any) -> Any:
        if self.check_event(AliasEvent):
            raise EagleError("YAML aliases are not supported; write values explicitly.")
        return super().compose_node(parent, index)


def unique_mapping(loader: UniqueLoader, node: Any, deep: bool = False) -> dict:
    result: dict = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        if not isinstance(key, str):
            raise EagleError("Metadata keys must be strings.")
        if key in result:
            raise EagleError(f"Duplicate YAML key: {key}")
        result[key] = loader.construct_object(value_node, deep=deep)
    return result


UniqueLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, unique_mapping)


def load_text(text: str) -> dict:
    if len(text.encode("utf-8")) > MAX_BYTES:
        raise EagleError("Metadata exceeds 64 KiB; link to data instead of embedding it.")
    try:
        data = yaml.load(text, Loader=UniqueLoader)
    except (yaml.YAMLError, RecursionError) as exc:
        raise EagleError("Invalid YAML; check indentation, nesting and value types.") from exc
    if not isinstance(data, dict):
        raise EagleError("Metadata must be a YAML mapping.")
    return data


def load(path: Path) -> dict:
    if path.is_symlink():
        raise EagleError(f"Refusing symlink metadata: {path.name}")
    try:
        if path.stat().st_size > MAX_BYTES:
            raise EagleError("Metadata exceeds 64 KiB.")
        return load_text(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError) as exc:
        raise EagleError(
            f"Cannot read {path.name}. Run connect-eagle init if it is missing."
        ) from exc


def schema() -> dict:
    return json.loads(files("connect_eagle").joinpath("schemas/project-v1.schema.json").read_text())


def errors(data: dict) -> list[str]:
    found = []
    for error in sorted(
        Draft202012Validator(schema()).iter_errors(data), key=lambda e: str(e.path)
    ):
        location = ".".join(map(str, error.absolute_path)) or "metadata"
        # Avoid embedding arbitrary field values in logs.
        if error.validator == "required":
            message = error.message
        elif error.validator == "additionalProperties":
            message = "Unknown field; see schema v1."
        else:
            message = f"Invalid value ({error.validator}); see schema v1."
        found.append(f"{location}: {message}")

    def walk(value: Any, path: str) -> None:
        if isinstance(value, dict):
            for key, child in value.items():
                walk(child, f"{path}.{key}")
        elif isinstance(value, list):
            for index, child in enumerate(value):
                walk(child, f"{path}.{index}")
        elif isinstance(value, str) and value.startswith("https://"):
            try:
                parts = urlsplit(value)
                if not parts.hostname or parts.username or parts.password or parts.query:
                    found.append(
                        f"{path}: URLs must be public, without credentials or query parameters."
                    )
                _ = parts.port
            except ValueError:
                found.append(f"{path}: Malformed URL.")

    walk(data, "metadata")
    if (
        data.get("schema") is True
        or data.get("schema") == 1.0
        and type(data.get("schema")) is float
    ):
        found.append("schema: Use the integer 1.")
    return found


def validate(data: dict) -> None:
    problems = errors(data)
    if problems:
        raise EagleError("Metadata validation failed:\n" + "\n".join(f"  - {p}" for p in problems))


def dump(data: dict) -> str:
    return yaml.safe_dump(data, sort_keys=False, allow_unicode=True)
