"""Validate an entire registry, then produce a deterministic JSON catalog."""

from __future__ import annotations

import json
from pathlib import Path

from .metadata import load, validate
from .repository import EagleError, public_url


def records(directory: Path) -> list[dict]:
    if not directory.is_dir() or directory.is_symlink():
        raise EagleError("Registry projects directory is missing or is a symlink.")
    found: list[dict] = []
    failures: list[str] = []
    slugs: set[str] = set()
    repositories: set[str] = set()
    for path in sorted(directory.iterdir()):
        if path.name in {"README.md", ".gitkeep"}:
            continue
        if path.is_symlink() or not path.is_file() or path.suffix != ".yml":
            failures.append(f"{path.name}: expected a regular <slug>.yml file.")
            continue
        try:
            data = load(path)
            validate(data)
            slug = data["project"]["slug"]
            repository = public_url(data["repository"]).casefold()
            if path.stem != slug:
                raise EagleError("Filename must match project.slug.")
            if slug in slugs or repository in repositories:
                raise EagleError("Duplicate slug or repository URL in registry.")
            slugs.add(slug)
            repositories.add(repository)
            found.append(data)
        except EagleError as exc:
            failures.append(f"{path.name}: {exc}")
    if failures:
        raise EagleError("Registry validation failed:\n" + "\n".join(failures))
    return sorted(found, key=lambda record: record["project"]["slug"])


def export(directory: Path, output: Path) -> int:
    data = records(directory)
    if output.exists() or output.is_symlink():
        raise EagleError("Catalog output already exists; choose a new output path.")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps({"schema": 1, "projects": data}, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return len(data)
