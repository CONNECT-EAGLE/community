from pathlib import Path

import pytest


def test_vendored_registry_contract_matches_cli():
    root = Path(__file__).resolve().parents[2]
    registry = root / "project-registry/validation/connect_eagle"
    if not registry.exists():
        pytest.skip(
            "Standalone CLI checkout; registry synchronization is checked in the foundation"
        )
    source = root / "connect-eagle-cli/src/connect_eagle"
    for name in [
        "__init__.py",
        "metadata.py",
        "repository.py",
        "registry.py",
        "schemas/project-v1.schema.json",
    ]:
        assert (source / name).read_bytes() == (registry / name).read_bytes(), name
