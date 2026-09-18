"""Independent registry validator; no package-index publication is required."""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "validation"))
from connect_eagle.registry import records, export  # noqa: E402
from connect_eagle.repository import EagleError  # noqa: E402


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", nargs="?", type=Path, default=Path("projects"))
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    try:
        count = export(args.directory, args.output) if args.output else len(records(args.directory))
    except (EagleError, OSError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print(f"Registry valid: {count} project(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
