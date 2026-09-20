"""GitHub CLI adapter: register one metadata file without touching project Git state."""

from __future__ import annotations

import base64
import hashlib
import json
import re
from pathlib import Path
from typing import Any

from .metadata import load_text, validate
from .repository import EagleError, command, public_url


def registry_name(value: str) -> str:
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]*/[A-Za-z0-9][A-Za-z0-9_.-]*", value):
        raise EagleError("Registry must be OWNER/REPOSITORY on github.com.")
    return value


class GitHub:
    def __init__(self, cwd: Path):
        self.cwd = cwd

    def auth(self) -> None:
        result = command(
            ["gh", "auth", "status", "--hostname", "github.com"], self.cwd, check=False
        )
        if result.returncode:
            raise EagleError(
                "GitHub authentication unavailable. Run gh auth login --hostname github.com."
            )

    def api(self, endpoint: str, method: str = "GET", payload: dict | None = None) -> Any:
        args = ["gh", "api", "--hostname", "github.com", endpoint, "--method", method]
        if payload is not None:
            args += ["--input", "-"]
        result = command(
            args, self.cwd, input_text=json.dumps(payload) if payload else None, timeout=60
        )
        try:
            return json.loads(result.stdout) if result.stdout.strip() else None
        except ValueError as exc:
            raise EagleError(
                "GitHub returned an unexpected response. Retry with a current gh version."
            ) from exc

    def submit_issue(self, hub: str, data: dict, content: str) -> str:
        """Open an owner-authored review request in an existing community hub."""
        registry_name(hub)
        validate(data)
        self.auth()
        username = self.api("user")["login"]
        upstream = self.api(f"repos/{hub}")
        if upstream.get("archived") or upstream.get("disabled"):
            raise EagleError("The selected hub is archived or disabled.")
        if not upstream.get("has_issues", False):
            raise EagleError("The selected hub does not have issues enabled.")
        identity = hashlib.sha256(public_url(data["repository"]).casefold().encode()).hexdigest()
        marker = f"<!-- connect-eagle-project:{identity} -->"
        snapshot = f"<!-- connect-eagle-snapshot:{hashlib.sha256(content.encode()).hexdigest()} -->"
        page = 1
        while True:
            issues = self.api(
                f"repos/{hub}/issues?state=open&creator={username}&per_page=100&page={page}"
            )
            for issue in issues:
                if "pull_request" in issue or issue.get("user", {}).get("login") != username:
                    continue
                body = issue.get("body") or ""
                if marker in body:
                    if snapshot in body:
                        return issue["html_url"]
                    raise EagleError(
                        f"An open submission already exists: {issue['html_url']}. "
                        "Update that issue with your revised metadata; no duplicate was created."
                    )
            if len(issues) < 100:
                break
            page += 1
        # A longer fence keeps user-authored metadata inside one literal code block.
        fence = "`" * max(3, 1 + max((len(s) for s in re.findall(r"`+", content)), default=0))
        issue = self.api(
            f"repos/{hub}/issues", "POST", {
                "title": f"Project submission: {data['project']['slug']}",
                "body": (
                    f"{marker}\n{snapshot}\n\n"
                    "## Project registration request\n\n"
                    f"Repository: {data['repository']}\n\n"
                    "This requests community review; it does not register the project yet.\n\n"
                    "### Maintainer authority\n\n"
                    "- [ ] I maintain this repository or have its maintainer's agreement.\n\n"
                    "Edit this issue to explain your authority and any missing license or citation. "
                    "Maintainers verify ownership and prepare a registry PR before acceptance.\n\n"
                    f"### Metadata snapshot\n\n{fence}yaml\n{content.rstrip()}\n{fence}\n\n"
                    "Registration preserves repository ownership and does not imply NASA endorsement."
                ),
            },
        )
        return issue["html_url"]

    def register(self, registry: str, data: dict, content: str) -> str:
        registry_name(registry)
        validate(data)
        self.auth()
        username = self.api("user")["login"]
        upstream = self.api(f"repos/{registry}")
        if upstream.get("archived") or upstream.get("disabled"):
            raise EagleError("The selected registry is archived or disabled.")
        base_branch = upstream["default_branch"]
        base = self.api(f"repos/{registry}/commits/{base_branch}")
        base_sha = base["sha"]
        base_tree = base["commit"]["tree"]["sha"]
        root_entries = self.api(f"repos/{registry}/git/trees/{base_tree}")["tree"]
        projects = next((e for e in root_entries if e["path"] == "projects"), None)
        if not projects or projects["type"] != "tree":
            raise EagleError(
                "Registry needs a projects/ directory on its default branch. "
                "Publish and merge the registry foundation first."
            )
        project_entries = self.api(f"repos/{registry}/git/trees/{projects['sha']}")["tree"]
        slug = data["project"]["slug"]
        path = f"projects/{slug}.yml"
        for entry in project_entries:
            if entry["path"].lower() in {f"{slug}.yml", f"{slug}.yaml"}:
                blob = self.api(f"repos/{registry}/git/blobs/{entry['sha']}")
                old = load_text(base64.b64decode(blob["content"]).decode("utf-8"))
                validate(old)
                if (
                    public_url(old["repository"]).casefold()
                    != public_url(data["repository"]).casefold()
                ):
                    raise EagleError(
                        "That registry slug belongs to another repository. Choose a different slug."
                    )
                if old == data:
                    return f"Already registered: https://github.com/{registry}/blob/{base_branch}/{path}"
                if entry["path"] != f"{slug}.yml":
                    raise EagleError(
                        "Existing entry has a noncanonical filename; ask registry maintainers to normalize it."
                    )
        target = registry
        head_owner = registry.split("/")[0]
        if not upstream.get("permissions", {}).get("push", False):
            fork = self.api(f"repos/{registry}/forks", "POST", {"default_branch_only": True})
            target = fork["full_name"]
            # Verify an existing same-name repository is genuinely the intended fork.
            fork_info = self.api(f"repos/{target}")
            if (
                fork_info.get("parent", {}).get("full_name", "").casefold() != registry.casefold()
                or target.split("/")[0].casefold() != username.casefold()
            ):
                raise EagleError(
                    "GitHub did not return your fork of the registry. Check fork access and retry."
                )
            head_owner = target.split("/")[0]
        digest = hashlib.sha256(content.encode()).hexdigest()[:12]
        branch = f"register/{slug}-{digest}"
        # List exact head PRs first: repeated submission is idempotent.
        prs = self.api(f"repos/{registry}/pulls?state=open&head={head_owner}:{branch}")
        if prs:
            return prs[0]["html_url"]
        tree = self.api(
            f"repos/{target}/git/trees",
            "POST",
            {
                "base_tree": base_tree,
                "tree": [{"path": path, "mode": "100644", "type": "blob", "content": content}],
            },
        )
        refs = self.api(f"repos/{target}/git/matching-refs/heads/{branch}")
        existing = next((ref for ref in refs if ref["ref"] == f"refs/heads/{branch}"), None)
        if existing:
            previous = self.api(f"repos/{target}/git/commits/{existing['object']['sha']}")
            if previous["tree"]["sha"] != tree["sha"]:
                raise EagleError(
                    "An interrupted submission branch has different content. "
                    "Inspect it in GitHub before retrying; no ref was overwritten."
                )
        else:
            commit = self.api(
                f"repos/{target}/git/commits",
                "POST",
                {
                    "message": f"feat(registry): register {slug}",
                    "tree": tree["sha"],
                    "parents": [base_sha],
                },
            )
            self.api(
                f"repos/{target}/git/refs",
                "POST",
                {
                    "ref": f"refs/heads/{branch}",
                    "sha": commit["sha"],
                },
            )
        pr = self.api(
            f"repos/{registry}/pulls",
            "POST",
            {
                "title": f"Register project: {slug}",
                "base": base_branch,
                "head": f"{head_owner}:{branch}",
                "body": "Registers the attached schema-v1 metadata snapshot.\n\n"
                f"Repository: {data['repository']}\n\n"
                "Maintainers: verify submitter authority and project ownership before merging. "
                "Registration does not transfer ownership or imply NASA endorsement.",
            },
        )
        return pr["html_url"]
