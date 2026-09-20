"""Small, explicit commands for project onboarding and registry maintenance."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Annotated

import typer

from . import __version__
from .github import GitHub, registry_name
from .metadata import dump, load, validate
from .registry import export, records
from .repository import EagleError, Repository, command, github_slug, public_url, slugify

app = typer.Typer(
    no_args_is_help=True,
    invoke_without_command=True,
    pretty_exceptions_enable=False,
    help="Connect your existing project to C.O.N.N.E.C.T. EAGLE.",
)
registry_app = typer.Typer(
    no_args_is_help=True, help="Validate registry entries and export a catalog."
)
app.add_typer(registry_app, name="registry")
PathOption = Annotated[Path, typer.Option("--path", help="Any directory inside the project.")]


@app.callback()
def callback(version: Annotated[bool, typer.Option("--version", is_eager=True)] = False) -> None:
    if version:
        typer.echo(f"connect-eagle {__version__}")
        raise typer.Exit()


def project_metadata(repo: Repository) -> dict:
    if (repo.root / ".connect-eagle.yaml").exists():
        raise EagleError("Conflicting .connect-eagle.yaml found; keep only .connect-eagle.yml.")
    data = load(repo.root / ".connect-eagle.yml")
    validate(data)
    return data


@app.command()
def init(
    path: PathOption = Path("."),
    name: str | None = None,
    description: str | None = None,
    mission: Annotated[
        str | None, typer.Option(help="VSWIR, TIR, both, or supporting-technology.")
    ] = None,
    project_type: Annotated[str | None, typer.Option("--type")] = None,
    topics: Annotated[str | None, typer.Option(help="Comma-separated topic tags.")] = None,
    collaborators: Annotated[
        bool | None, typer.Option("--collaborators/--no-collaborators")
    ] = None,
    repository: str | None = None,
    remote: str | None = None,
    non_interactive: Annotated[bool, typer.Option("--non-interactive", "--yes")] = False,
) -> None:
    """Infer project details and create metadata; existing files are never replaced."""
    repo = Repository.discover(path)
    target = repo.root / ".connect-eagle.yml"
    if target.exists() or target.is_symlink() or (repo.root / ".connect-eagle.yaml").exists():
        raise EagleError("Metadata already exists. Edit it directly, then run doctor.")
    inferred = repo.infer()
    url = public_url(repository) if repository else repo.choose_url(remote)
    interactive = not non_interactive and sys.stdin.isatty()
    if not url and interactive:
        url = public_url(typer.prompt("Public repository URL"))
    if not url:
        raise EagleError(
            "Cannot infer a public repository URL. Pass --repository https://host/owner/repo."
        )
    project_name = name or inferred.get("name") or url.rsplit("/", 1)[-1] or repo.root.name
    description = description or inferred.get("description")
    if not description and interactive:
        description = typer.prompt("One-sentence project description")
    if not mission and interactive:
        mission = typer.prompt("EAGLE area (VSWIR / TIR / both / supporting-technology)")
    if not description or not mission:
        raise EagleError(
            "Provide --description and --mission when they cannot be inferred non-interactively."
        )
    if project_type is None:
        project_type = (
            typer.prompt(
                "Type (research / software / dataset / tutorial / working-group)",
                default="research",
            )
            if interactive
            else "research"
        )
    if collaborators is None:
        collaborators = (
            typer.confirm("Are collaborators welcome?", default=False) if interactive else False
        )
    if topics is None:
        topics = (
            typer.prompt("Topic tags, comma-separated", default="remote-sensing")
            if interactive
            else ""
        )
    area = mission.strip().lower()
    missions = {
        "vswir": ["VSWIR"],
        "tir": ["TIR"],
        "both": ["VSWIR", "TIR"],
        "supporting-technology": ["supporting-technology"],
        "supporting": ["supporting-technology"],
    }.get(area)
    if missions is None:
        raise EagleError("--mission must be VSWIR, TIR, both, or supporting-technology.")
    data = {
        "schema": 1,
        "project": {
            "name": project_name,
            "slug": slugify(project_name),
            "description": description,
        },
        "eagle": {
            "mission": missions,
            "topics": list(
                dict.fromkeys(slugify(t.strip()) for t in topics.split(",") if t.strip())
            ),
        },
        "project_type": project_type,
        "status": "active",
        "collaboration": {"open": collaborators, "looking_for": []},
        "repository": url,
    }
    if inferred.get("license"):
        data["license"] = inferred["license"]
    citation = repo.file("CITATION.cff")
    if citation:
        data["citation"] = {"cff": citation.name}
    validate(data)
    with target.open("x", encoding="utf-8", newline="\n") as stream:
        stream.write(dump(data))
    typer.echo(f"Created {target}\nReview it, then run connect-eagle doctor.")


@app.command()
def status(path: PathOption = Path(".")) -> None:
    """Show repository readiness; registry acceptance is not inferred offline."""
    repo = Repository.discover(path)
    metadata_state = "Missing"
    collaboration = "Unknown"
    try:
        data = project_metadata(repo)
        metadata_state = "Valid (schema 1)"
        collaboration = "Yes" if data["collaboration"]["open"] else "No"
    except EagleError as exc:
        metadata_state = str(exc)
    receipt = repo.git_dir / "connect-eagle" / "receipt.json"
    registry_state = "Unknown (offline; no local submission receipt)"
    if receipt.is_file():
        try:
            registry_state = "Local submission receipt: " + json.loads(receipt.read_text())["url"]
        except (ValueError, KeyError, OSError):
            registry_state = "Unreadable local receipt; remote state unknown"
    checks = [
        ("Git repository", str(repo.root)),
        (
            "GitHub remote",
            "Yes" if any(github_slug(public_url(u)) for u in repo.remotes.values()) else "No",
        ),
        ("Metadata", metadata_state),
        (
            "README",
            "Yes" if repo.file("README.md", "README.rst", "README", "README.txt") else "Missing",
        ),
        (
            "License",
            "Yes" if repo.file("LICENSE", "LICENSE.md", "LICENSE.txt", "COPYING") else "Missing",
        ),
        ("Citation", "Yes" if repo.file("CITATION.cff") else "Missing (recommended)"),
        ("Registry status", registry_state),
        ("Open collaboration", collaboration),
    ]
    typer.echo("C.O.N.N.E.C.T. EAGLE\n")
    for label, value in checks:
        typer.echo(f"{label:22} {value}")


@app.command()
def doctor(path: PathOption = Path("."), online: bool = False, strict: bool = False) -> None:
    """Diagnose issues. --online checks remote access and GitHub authentication."""
    repo = Repository.discover(path)
    failures = repo.unsafe_states()
    warnings = []
    try:
        data = project_metadata(repo)
        urls = {public_url(url) for url in repo.remotes.values()}
        if urls and data["repository"] not in urls:
            warnings.append(
                "Metadata URL does not match a detected remote; confirm the intended repository."
            )
        if (
            data.get("citation", {}).get("cff")
            and not (repo.root / data["citation"]["cff"]).is_file()
        ):
            warnings.append("Citation path does not exist; update citation.cff in metadata.")
    except EagleError as exc:
        failures.append(str(exc))
    for names, fix in [
        (
            ("README.md", "README.rst", "README", "README.txt"),
            "Add a README describing use and contribution.",
        ),
        (
            ("LICENSE", "LICENSE.md", "LICENSE.txt", "COPYING"),
            "Choose and add a license; registration does not grant reuse rights.",
        ),
        (("CITATION.cff",), "Add CITATION.cff to make scientific attribution easier."),
    ]:
        if not repo.file(*names):
            warnings.append(fix)
    if not repo.remotes:
        warnings.append("No Git remotes. Add one or specify --repository during init.")
    for remote_name, raw in repo.remotes.items():
        if public_url(raw) is None:
            warnings.append(
                f"Remote {remote_name}: no web URL inferred (local remotes are supported)."
            )
        if online:
            result = command(
                ["git", "ls-remote", "--", remote_name, "HEAD"], repo.root, check=False
            )
            if result.returncode:
                failures.append(
                    f"Remote {remote_name} is unreachable; inspect its URL and credentials."
                )
    if online and any(github_slug(public_url(u)) for u in repo.remotes.values()):
        try:
            GitHub(repo.root).auth()
        except EagleError as exc:
            failures.append(str(exc))
    for issue in failures:
        typer.echo(f"ERROR  {issue}")
    for issue in warnings:
        typer.echo(f"WARN   {issue}")
    if not online:
        typer.echo(
            "INFO   Remote reachability and GitHub authentication not checked; use --online."
        )
    typer.echo(f"Doctor: {len(failures)} error(s), {len(warnings)} warning(s).")
    if failures or (strict and warnings):
        raise typer.Exit(1)


@app.command()
def submit(
    path: PathOption = Path("."),
    registry: Annotated[str | None, typer.Option(envvar="CONNECT_EAGLE_REGISTRY")] = None,
    push: Annotated[
        bool, typer.Option(help="Create a registry branch and GitHub pull request.")
    ] = False,
    issue: Annotated[
        bool, typer.Option(help="Open a project review issue in --registry OWNER/HUB.")
    ] = False,
    dry_run: bool = False,
) -> None:
    """Prepare a packet; --issue opens hub review; --push opens a dedicated-registry PR."""
    if push and issue:
        raise EagleError("Choose either --issue for hub review or --push for a registry PR.")
    repo = Repository.discover(path)
    problems = repo.unsafe_states()
    if problems:
        raise EagleError("\n".join(problems))
    data = project_metadata(repo)
    if registry:
        registry_name(registry)
    if (push or issue) and not registry:
        raise EagleError(
            "--issue/--push requires --registry OWNER/REPOSITORY or CONNECT_EAGLE_REGISTRY."
        )
    slug = data["project"]["slug"]
    typer.echo(
        f"Project: {slug}\nRecord: projects/{slug}.yml\nRegistry: {registry or 'not selected'}"
    )
    typer.echo("Route: " + ("review issue" if issue else "registry PR" if push else "local packet"))
    if dry_run:
        typer.echo("Dry run: validated; no files or remote resources changed.")
        return
    content = dump(data)
    if push or issue:
        client = GitHub(repo.root)
        url = (
            client.submit_issue(registry, data, content)
            if issue else client.register(registry, data, content)
        )
        destination = repo.git_dir / "connect-eagle"
        destination.mkdir(parents=True, exist_ok=True)
        (destination / "receipt.json").write_text(
            json.dumps({"registry": registry, "url": url}) + "\n", encoding="utf-8"
        )
        typer.echo(url)
        if issue:
            typer.echo("Review requested, not yet registered. Complete the authority section in the issue.")
    else:
        destination = repo.git_dir / "connect-eagle" / "submissions" / slug
        destination.mkdir(parents=True, exist_ok=True)
        (destination / f"{slug}.yml").write_text(content, encoding="utf-8")
        (destination / "PR_BODY.md").write_text(
            f"Register {data['project']['name']}\n\nRepository: {data['repository']}\n\n"
            "Review project ownership, metadata and collaboration preferences before merging.\n",
            encoding="utf-8",
        )
        typer.echo(
            f"Prepared {destination}\nFor CONNECT EAGLE review: connect-eagle submit "
            "--registry CONNECT-EAGLE/testrepo --issue\n"
            "For a dedicated registry PR: connect-eagle submit --registry OWNER/project-registry --push"
        )


@registry_app.command("validate")
def validate_registry(directory: Path = Path("projects")) -> None:
    """Validate every project, filename, slug and repository identity."""
    typer.echo(f"Registry valid: {len(records(directory))} project(s).")


@registry_app.command("export")
def export_registry(
    directory: Path = Path("projects"), output: Path = Path("catalog.json")
) -> None:
    """Export validated records for a future website/API."""
    typer.echo(f"Exported {export(directory, output)} project(s) to {output}.")


def main() -> None:
    try:
        app()
    except (EagleError, OSError) as exc:
        typer.echo(f"Error: {exc}", err=True)
        raise SystemExit(1) from None


if __name__ == "__main__":
    main()
