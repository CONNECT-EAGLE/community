import base64
import hashlib

import pytest

from connect_eagle.github import GitHub, registry_name
from connect_eagle.metadata import dump
from connect_eagle.repository import EagleError


class FakeGitHub(GitHub):
    def __init__(
        self, cwd, *, fork=False, old=None, existing_pr=False, wrong_fork=False, fail_pr=False
    ):
        super().__init__(cwd)
        self.calls = []
        self.fork = fork
        self.old = old
        self.existing_pr = existing_pr
        self.wrong_fork = wrong_fork
        self.fail_pr = fail_pr
        self.refs = []

    def auth(self):
        self.calls.append(("auth", None, None))

    def api(self, endpoint, method="GET", payload=None):
        self.calls.append((endpoint, method, payload))
        if endpoint == "user":
            return {"login": "alice"}
        if endpoint == "repos/lab/registry":
            return {"default_branch": "main", "permissions": {"push": not self.fork}}
        if endpoint.endswith("/commits/main"):
            return {"sha": "base", "commit": {"tree": {"sha": "root"}}}
        if endpoint.endswith("/git/trees/root"):
            return {"tree": [{"path": "projects", "type": "tree", "sha": "projects"}]}
        if endpoint.endswith("/git/trees/projects"):
            return {"tree": [{"path": "forest-tools.yml", "sha": "old"}] if self.old else []}
        if endpoint.endswith("/git/blobs/old"):
            return {"content": base64.b64encode(dump(self.old).encode()).decode()}
        if endpoint.endswith("/forks"):
            return {"full_name": "alice/registry"}
        if endpoint == "repos/alice/registry":
            return {"parent": {"full_name": "wrong/repo" if self.wrong_fork else "lab/registry"}}
        if "/pulls?" in endpoint:
            return (
                [{"html_url": "https://github.com/lab/registry/pull/7"}] if self.existing_pr else []
            )
        if endpoint.endswith("/git/trees"):
            return {"sha": "new-tree"}
        if "/git/matching-refs/" in endpoint:
            return self.refs
        if endpoint.endswith("/git/commits/new-commit"):
            return {"tree": {"sha": "new-tree"}}
        if endpoint.endswith("/git/commits"):
            return {"sha": "new-commit"}
        if endpoint.endswith("/git/refs"):
            self.refs.append({"ref": payload["ref"], "object": {"sha": "new-commit"}})
            return {}
        if endpoint.endswith("/pulls"):
            if self.fail_pr:
                self.fail_pr = False
                raise EagleError("Simulated network interruption")
            return {"html_url": "https://github.com/lab/registry/pull/7"}
        raise AssertionError((endpoint, method, payload))


@pytest.mark.parametrize("fork", [False, True])
def test_registration_single_file_and_no_force(tmp_path, record, fork):
    client = FakeGitHub(tmp_path, fork=fork)
    content = dump(record)
    assert client.register("lab/registry", record, content).endswith("/pull/7")
    writes = [(e, p) for e, method, p in client.calls if method == "POST"]
    tree = next(p for e, p in writes if e.endswith("/git/trees"))
    assert tree["base_tree"] == "root"
    assert tree["tree"] == [
        {"path": "projects/forest-tools.yml", "mode": "100644", "type": "blob", "content": content}
    ]
    assert not any(method in {"PATCH", "DELETE", "PUT"} for _, method, _ in client.calls)
    assert not any(p.get("force") for _, p in writes)
    assert writes[-1][1]["head"].startswith("alice:" if fork else "lab:")
    assert writes[-1][1]["base"] == "main"


def test_unchanged_registration_does_not_write(tmp_path, record):
    client = FakeGitHub(tmp_path, old=record)
    assert client.register("lab/registry", record, dump(record)).startswith("Already registered")
    assert not any(method == "POST" for _, method, _ in client.calls)


def test_collision_refuses_overwrite(tmp_path, record):
    old = dict(record, repository="https://github.com/someone/another-project")
    client = FakeGitHub(tmp_path, old=old)
    with pytest.raises(EagleError, match="another repository"):
        client.register("lab/registry", record, dump(record))
    assert not any(method == "POST" for _, method, _ in client.calls)


def test_idempotent_open_pr(tmp_path, record):
    client = FakeGitHub(tmp_path, existing_pr=True)
    assert client.register("lab/registry", record, dump(record)).endswith("/pull/7")
    assert not any(method == "POST" for _, method, _ in client.calls)


def test_resume_interrupted_pr_without_overwriting_ref(tmp_path, record):
    client = FakeGitHub(tmp_path, fail_pr=True)
    with pytest.raises(EagleError, match="interruption"):
        client.register("lab/registry", record, dump(record))
    client.calls.clear()
    assert client.register("lab/registry", record, dump(record)).endswith("/pull/7")
    assert not any(endpoint.endswith("/git/refs") for endpoint, _, _ in client.calls)


def test_reject_unrelated_fork(tmp_path, record):
    client = FakeGitHub(tmp_path, fork=True, wrong_fork=True)
    with pytest.raises(EagleError, match="your fork"):
        client.register("lab/registry", record, dump(record))
    assert not any(endpoint.endswith("/git/trees") for endpoint, _, _ in client.calls)


@pytest.mark.parametrize(
    "value",
    ["../bad", "https://github.com/lab/repo", "lab/repo?token=x", "lab/repo/path", "-bad/repo"],
)
def test_invalid_registry(value):
    with pytest.raises(EagleError):
        registry_name(value)


def test_branch_contains_content_digest(tmp_path, record):
    client = FakeGitHub(tmp_path)
    content = dump(record)
    client.register("lab/registry", record, content)
    digest = hashlib.sha256(content.encode()).hexdigest()[:12]
    assert client.refs[0]["ref"] == f"refs/heads/register/forest-tools-{digest}"
