"""Build the public project directory from validated registry records."""

from __future__ import annotations

import argparse
import html
import sys
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "connect-eagle-foundation/project-registry/validation"))
from connect_eagle.registry import records


def plain(value: str) -> str:
    value = html.escape(str(value), quote=False).replace("|", "&#124;")
    for char in "\\`*_[]":
        value = value.replace(char, "\\" + char)
    return value


def render(projects: list[dict]) -> str:
    lines = [
        "# Projects and tools",
        "",
        (
            "[Home](README.md) · [Submit a project](SUBMIT_PROJECT.md) · "
            "[Open opportunities](OPPORTUNITIES.md)"
        ),
        "",
        (
            "This directory is generated from reviewed registry records. "
            "Infrastructure below is listed separately and is not a scientific-project endorsement."
        ),
        "",
        "## Community infrastructure",
        "",
        (
            "Current setup contact: [Fares Alhezaimi (@falhezaimi)](https://github.com/falhezaimi). "
            "These components live in this repository; separate repositories are not required to contribute."
        ),
        "",
        "| Component | Purpose | Relevance | Type | Status | Contributions |",
        "| --- | --- | --- | --- | --- | --- |",
        "| [Community hub](README.md) | Onboarding, opportunities, and shared learning | Supporting EO | Community | Incubating | [Open tasks](OPPORTUNITIES.md) |",
        "| [connect-eagle CLI](connect-eagle-foundation/connect-eagle-cli/README.md) | Prepare and validate project metadata | VSWIR / TIR / supporting EO | Software | Incubating, usable v0.1 | Documentation, examples, testing |",
        "| [Project registry](connect-eagle-foundation/project-registry/README.md) | Review project records and build this directory | VSWIR / TIR / supporting EO | Catalog | Incubating | Review and register projects |",
        "| [Project templates](connect-eagle-foundation/templates/README.md) | Five starting points for research, software, data, tutorials and groups | Supporting EO | Education / templates | Incubating | Examples and scientific review |",
        "",
        "## Registered projects",
        "",
        (
            f"Accepted registry entries: **{len(projects)}**. "
            "Only merged records appear here. [Connect your project](SUBMIT_PROJECT.md)."
        ),
        "",
    ]
    groups = [
        ("Active projects", lambda p: p["status"] == "active"),
        ("Tools", lambda p: p["project_type"] == "software"),
        ("Datasets", lambda p: p["project_type"] == "dataset"),
        ("Education", lambda p: p["project_type"] == "tutorial"),
        ("Research", lambda p: p["project_type"] in {"research", "working-group"}),
        ("VSWIR", lambda p: "VSWIR" in p["eagle"]["mission"]),
        ("TIR", lambda p: "TIR" in p["eagle"]["mission"]),
        (
            "Multi-sensor / supporting EO",
            lambda p: (
                "supporting-technology" in p["eagle"]["mission"]
                or {"VSWIR", "TIR"}.issubset(p["eagle"]["mission"])
            ),
        ),
        (
            "Open for collaboration",
            lambda p: (
                p["collaboration"]["open"]
                and p["status"] not in {"completed", "archived"}
            ),
        ),
        ("All registered projects", lambda p: True),
    ]
    for title, matches in groups:
        selected = [p for p in projects if matches(p)]
        lines.extend([f"## {title}", ""])
        if not selected:
            lines.extend(["No accepted registry entries in this category yet.", ""])
            continue
        lines.extend(
            [
                "| Name | Description | Relevance | Type | Status | Maintainer | Repository | Open to contributors? |",
                "| --- | --- | --- | --- | --- | --- | --- | --- |",
            ]
        )
        for p in selected:
            maintainers = (
                ", ".join(m["name"] for m in p.get("maintainers", [])) or "Not supplied"
            )
            url = quote(p["repository"], safe="/:@%+.-_~")
            collaboration = "Yes" if p["collaboration"]["open"] else "No"
            if p["status"] in {"completed", "archived"}:
                collaboration = (
                    "Confirm with maintainer" if p["collaboration"]["open"] else "No"
                )
            cells = [
                p["project"]["name"],
                p["project"]["description"],
                ", ".join(p["eagle"]["mission"]),
                p["project_type"],
                p["status"],
                maintainers,
            ]
            lines.append(
                "| "
                + " | ".join(plain(c) for c in cells)
                + f" | [Repository]({url}) | {collaboration} |"
            )
        lines.append("")
    lines.extend(
        [
            "## Historical work",
            "",
            (
                "[CONNECT-SBG history](HISTORY.md) is preserved separately. "
                "Historical analyses are not automatically registered or labeled active."
            ),
            "",
            "## Keep this directory current",
            "",
            (
                "Edit the registry YAML, then run `python connect-eagle-foundation/scripts/build_directory.py` "
                "from the repository root. CI uses `--check` to detect drift. See [submission instructions](SUBMIT_PROJECT.md)."
            ),
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    content = render(
        records(ROOT / "connect-eagle-foundation/project-registry/projects")
    )
    output = ROOT / "PROJECTS.md"
    if args.check:
        if not output.exists() or output.read_text(encoding="utf-8") != content:
            print(
                "PROJECTS.md is out of date; run build_directory.py and commit the result."
            )
            return 1
    else:
        output.write_text(content, encoding="utf-8")
    print("Project directory matches the registry.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
