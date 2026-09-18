import copy

import pytest

from connect_eagle.metadata import dump, load_text, validate
from connect_eagle.registry import export, records
from connect_eagle.repository import EagleError


def test_valid_roundtrip(record):
    validate(record)
    assert load_text(dump(record)) == record


@pytest.mark.parametrize(
    "text",
    [
        "schema: 1\nschema: 2",
        "a: &a [*a]",
        "[]",
        "!!python/object:os.system {}",
        "a: [",
        "a: " + "x" * 65536,
        "[a, b]: c",
        "1: value",
    ],
    # Pytest stores the case ID in PYTEST_CURRENT_TEST. Keep the oversized
    # document out of that ID so Windows can set the environment variable.
    ids=["duplicate-key", "alias", "sequence", "unsafe-tag", "syntax", "oversized",
         "complex-key", "non-string-key"],
)
def test_invalid_yaml(text):
    with pytest.raises(EagleError):
        load_text(text)


@pytest.mark.parametrize(
    "field,value",
    [
        ("schema", 2),
        ("schema", True),
        ("schema", 1.0),
        ("status", "unknown"),
        ("repository", "http://github.com/x/y"),
        ("repository", "https://token@github.com/x/y"),
        ("repository", "https://github.com/x/y?token=abc"),
        ("project_type", "science"),
    ],
)
def test_schema_rejects_invalid_fields(record, field, value):
    record[field] = value
    with pytest.raises(EagleError):
        validate(record)


def test_unknown_fields_and_traversal(record):
    record["unknown"] = "ignored by permissive validators"
    with pytest.raises(EagleError):
        validate(record)
    del record["unknown"]
    record["project"]["slug"] = "../escape"
    with pytest.raises(EagleError):
        validate(record)


def test_registry_catalog_and_collisions(tmp_path, record):
    projects = tmp_path / "projects"
    projects.mkdir()
    (projects / "forest-tools.yml").write_text(dump(record))
    assert len(records(projects)) == 1
    output = tmp_path / "catalog.json"
    assert export(projects, output) == 1
    with pytest.raises(EagleError, match="already exists"):
        export(projects, output)
    other = copy.deepcopy(record)
    other["project"]["slug"] = "other"
    other["repository"] = "https://GitHub.com/Example/Forest-Tools.git/"
    (projects / "other.yml").write_text(dump(other))
    with pytest.raises(EagleError, match="Duplicate"):
        records(projects)


def test_registry_filename_and_symlink(tmp_path, record):
    (tmp_path / "wrong.yml").write_text(dump(record))
    with pytest.raises(EagleError, match="Filename"):
        records(tmp_path)
    (tmp_path / "wrong.yml").unlink()
    target = tmp_path.parent / "external.yml"
    target.write_text(dump(record))
    try:
        (tmp_path / "forest-tools.yml").symlink_to(target)
    except OSError:
        pytest.skip("Symlinks not enabled on this platform")
    with pytest.raises(EagleError, match="regular"):
        records(tmp_path)
