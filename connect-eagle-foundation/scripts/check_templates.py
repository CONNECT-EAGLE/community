"""Validate example metadata while keeping examples out of the live registry."""

from pathlib import Path

from connect_eagle.metadata import load, validate

root = Path(__file__).resolve().parents[1]
examples = sorted((root / "templates").glob("*/.connect-eagle.yml.example"))
assert len(examples) == 5, "Expected five project types"
for example in examples:
    validate(load(example))
print(f"Validated {len(examples)} template metadata examples.")
