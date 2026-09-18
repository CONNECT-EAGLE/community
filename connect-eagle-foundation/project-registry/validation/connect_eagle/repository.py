"""Read-only Git discovery. Never execute project code or modify Git configuration."""

from __future__ import annotations

import json
import os
import re
import subprocess
import tomllib
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit


class EagleError(Exception):
    """A recoverable, user-facing error."""


def command(
    args: list[str],
    cwd: Path,
    *,
    input_text: str | None = None,
    timeout: int = 30,
    check: bool = True,
) -> subprocess.CompletedProcess[str]:
    try:
        result = subprocess.run(
            args,
            cwd=cwd,
            input=input_text,
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=timeout,
            check=False,
            env={**os.environ, "GIT_TERMINAL_PROMPT": "0", "GH_PROMPT_DISABLED": "1"},
        )
    except FileNotFoundError as exc:
        raise EagleError(f"Install {args[0]} and ensure it is on PATH.") from exc
    except subprocess.TimeoutExpired as exc:
        raise EagleError(
            f"{args[0]} timed out after {timeout}s; check connectivity and retry."
        ) from exc
    if check and result.returncode:
        # Do not echo subprocess output: a remote or authentication error may contain credentials.
        raise EagleError(
            f"{args[0]} {args[1]} failed (exit {result.returncode}). "
            "Check the repository, access and authentication."
        )
    return result


def public_url(remote: str) -> str | None:
    """Convert common SSH/HTTPS remotes to a credential-free web repository URL."""
    remote = remote.strip()
    scp = re.fullmatch(r"(?:[^/@:]+@)?([A-Za-z0-9.-]+):([^\s]+)", remote)
    if scp and "://" not in remote:
        # A Windows drive letter is not an SSH host.
        if len(scp[1]) == 1 or "/" not in scp[2]:
            return None
        remote = f"ssh://{scp[1]}/{scp[2]}"
    try:
        parts = urlsplit(remote)
        if parts.scheme not in {"https", "http", "ssh", "git"} or not parts.hostname:
            return None
        host = parts.hostname.lower()
        path = parts.path.rstrip("/").removesuffix(".git")
        if len(path.strip("/").split("/")) < 2 or any(c.isspace() for c in path):
            return None
        # URL ports matter for HTTP Git hosting, but SSH ports are transport-only.
        port = parts.port if parts.scheme in {"http", "https"} else None
        authority = host + (f":{port}" if port else "")
        return urlunsplit(("https", authority, path, "", ""))
    except ValueError:
        return None


def github_slug(url: str | None) -> str | None:
    if not url:
        return None
    parts = urlsplit(url)
    if parts.netloc.lower() != "github.com":
        return None
    path = parts.path.strip("/")
    return path if re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", path) else None


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")[:80].rstrip("-")
    if not slug:
        raise EagleError("Project name needs an ASCII slug; pass --name with letters or digits.")
    return slug


@dataclass(frozen=True)
class Repository:
    root: Path
    git_dir: Path
    remotes: dict[str, str]
    branch: str | None
    has_commits: bool

    @classmethod
    def discover(cls, path: Path) -> Repository:
        cwd = path.resolve()
        result = command(["git", "rev-parse", "--show-toplevel"], cwd, check=False)
        if result.returncode:
            raise EagleError(
                "This is not a Git working tree. Run from your project or use git init."
            )
        root = Path(result.stdout.strip()).resolve()
        git_dir = Path(command(["git", "rev-parse", "--absolute-git-dir"], root).stdout.strip())
        names = command(["git", "remote"], root).stdout.splitlines()
        remotes = {
            n: command(["git", "remote", "get-url", "--", n], root).stdout.strip() for n in names
        }
        branch = (
            command(
                ["git", "symbolic-ref", "--quiet", "--short", "HEAD"], root, check=False
            ).stdout.strip()
            or None
        )
        has_commits = (
            command(["git", "rev-parse", "--verify", "HEAD"], root, check=False).returncode == 0
        )
        return cls(root, git_dir, remotes, branch, has_commits)

    def choose_url(self, remote_name: str | None = None) -> str | None:
        if remote_name:
            if remote_name not in self.remotes:
                raise EagleError(f"Remote {remote_name!r} does not exist.")
            return public_url(self.remotes[remote_name])
        if "origin" in self.remotes:
            return public_url(self.remotes["origin"])
        urls = {u for r in self.remotes.values() if (u := public_url(r))}
        if len(urls) > 1:
            raise EagleError(
                "Multiple remotes without origin. Choose --remote NAME or --repository URL."
            )
        return next(iter(urls), None)

    def file(self, *names: str) -> Path | None:
        wanted = {n.lower() for n in names}
        return next(
            (
                p
                for p in sorted(self.root.iterdir())
                if p.name.lower() in wanted and p.is_file() and not p.is_symlink()
            ),
            None,
        )

    def unsafe_states(self) -> list[str]:
        states = []
        if self.branch is None and self.has_commits:
            states.append("Detached HEAD: switch to a named branch before submitting.")
        for marker in (
            "MERGE_HEAD",
            "rebase-merge",
            "rebase-apply",
            "CHERRY_PICK_HEAD",
            "REVERT_HEAD",
        ):
            if (self.git_dir / marker).exists():
                states.append(f"Git operation in progress ({marker}); finish or abort it first.")
        if command(["git", "ls-files", "-u"], self.root).stdout.strip():
            states.append("Unresolved merge conflicts; resolve them first.")
        return states

    def infer(self) -> dict[str, str]:
        result: dict[str, str] = {}
        try:
            pyproject = self.file("pyproject.toml")
            if pyproject:
                data = tomllib.loads(pyproject.read_text(encoding="utf-8"))
                project = data.get("project", {}) or data.get("tool", {}).get("poetry", {})
                for key in ("name", "description"):
                    if isinstance(project.get(key), str):
                        result[key] = project[key]
            package = self.file("package.json")
            if package:
                data = json.loads(package.read_text(encoding="utf-8"))
                for key in ("name", "description"):
                    if isinstance(data.get(key), str):
                        result.setdefault(key, data[key])
            description = self.file("DESCRIPTION")
            if description:
                data = dict(
                    re.findall(
                        r"^(Package|Title):\s*(.+)$",
                        description.read_text(encoding="utf-8"),
                        re.MULTILINE,
                    )
                )
                if data.get("Package"):
                    result.setdefault("name", data["Package"])
                if data.get("Title"):
                    result.setdefault("description", data["Title"])
        except (OSError, ValueError, TypeError, AttributeError) as exc:
            raise EagleError(
                "Project metadata is malformed; fix pyproject.toml, package.json or DESCRIPTION."
            ) from exc
        readme = self.file("README.md", "README.rst", "README", "README.txt")
        if readme:
            for line in readme.read_text(encoding="utf-8", errors="replace").splitlines():
                line = line.strip()
                if line and not line.startswith(("#", "[", "!", "<", "```", "==", "--")):
                    result.setdefault("description", line[:500])
                    break
        license_file = self.file("LICENSE", "LICENSE.md", "LICENSE.txt", "COPYING")
        if license_file:
            body = license_file.read_text(encoding="utf-8", errors="replace")
            if "MIT License" in body and "Permission is hereby granted" in body:
                result["license"] = "MIT"
            elif "Apache License" in body and "Version 2.0" in body:
                result["license"] = "Apache-2.0"
            else:
                result["license"] = f"LicenseRef-{license_file.name.replace('.', '-')}"
        return result
