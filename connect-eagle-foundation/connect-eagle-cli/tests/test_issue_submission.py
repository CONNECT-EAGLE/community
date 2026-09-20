import copy
import json

import pytest
from typer.testing import CliRunner

from connect_eagle.cli import app
from connect_eagle.github import GitHub
from connect_eagle.metadata import dump
from connect_eagle.repository import EagleError


class IssueGitHub(GitHub):
    def __init__(self, cwd, *, enabled=True, archived=False):
        super().__init__(cwd)
        self.enabled = enabled
        self.archived = archived
        self.issues = []
        self.calls = []

    def auth(self):
        pass

    def api(self, endpoint, method="GET", payload=None):
        self.calls.append((endpoint, method, payload))
        if endpoint == "user":
            return {"login": "alice"}
        if endpoint == "repos/community/hub":
            return {"has_issues": self.enabled, "archived": self.archived}
        if endpoint.startswith("repos/community/hub/issues?"):
            page = int(endpoint.rsplit("=", 1)[1])
            return self.issues[(page - 1) * 100:page * 100]
        if endpoint == "repos/community/hub/issues" and method == "POST":
            issue = dict(payload, html_url="https://github.com/community/hub/issues/1",
                         user={"login": "alice"})
            self.issues.append(issue)
            return issue
        raise AssertionError((endpoint, method, payload))


def test_issue_route_creates_review_request_and_reuses_it(tmp_path, record):
    client = IssueGitHub(tmp_path)
    content = dump(record)
    url = client.submit_issue("community/hub", record, content)
    assert client.submit_issue("community/hub", record, content) == url
    writes = [(e, m, p) for e, m, p in client.calls if m != "GET"]
    assert len(writes) == 1
    assert writes[0][0] == "repos/community/hub/issues"
    body = writes[0][2]["body"]
    assert content.rstrip() in body
    assert "- [ ] I maintain" in body
    assert "does not register the project yet" in body


def test_revised_submission_does_not_duplicate_or_overwrite(tmp_path, record):
    client = IssueGitHub(tmp_path)
    client.submit_issue("community/hub", record, dump(record))
    revised = copy.deepcopy(record)
    revised["project"]["description"] = "Revised description."
    with pytest.raises(EagleError, match="Update that issue"):
        client.submit_issue("community/hub", revised, dump(revised))
    assert len(client.issues) == 1


def test_issue_search_paginates_and_ignores_pull_requests(tmp_path, record):
    client = IssueGitHub(tmp_path)
    url = client.submit_issue("community/hub", record, dump(record))
    original = client.issues[0]
    unrelated = dict(original, pull_request={}, html_url="wrong")
    client.issues = [unrelated] * 100 + [original]
    assert client.submit_issue("community/hub", record, dump(record)) == url
    assert any(e.endswith("page=2") for e, _, _ in client.calls)


@pytest.mark.parametrize("options", [{"enabled": False}, {"archived": True}])
def test_unavailable_hub_has_no_writes(tmp_path, record, options):
    client = IssueGitHub(tmp_path, **options)
    with pytest.raises(EagleError):
        client.submit_issue("community/hub", record, dump(record))
    assert all(method == "GET" for _, method, _ in client.calls)


def test_metadata_with_backticks_stays_inside_literal_fence(tmp_path, record):
    record["project"]["description"] = "Example ``` text."
    client = IssueGitHub(tmp_path)
    client.submit_issue("community/hub", record, dump(record))
    assert "````yaml\n" in client.issues[0]["body"]


def test_issue_cli_dry_run_receipt_and_git_preservation(git_repo, monkeypatch):
    runner = CliRunner()
    assert runner.invoke(app, ["init", "--path", str(git_repo), "--non-interactive",
                               "--mission", "both", "--description", "Satellite tools."]).exit_code == 0
    config_before = (git_repo / ".git/config").read_bytes()
    metadata_before = (git_repo / ".connect-eagle.yml").read_bytes()
    calls = []

    def submit(self, hub, data, content):
        calls.append((hub, data, content))
        return "https://github.com/community/hub/issues/1"

    monkeypatch.setattr(GitHub, "submit_issue", submit)
    args = ["submit", "--path", str(git_repo), "--registry", "community/hub", "--issue"]
    assert runner.invoke(app, args + ["--dry-run"]).exit_code == 0
    assert not calls
    assert not (git_repo / ".git/connect-eagle").exists()
    result = runner.invoke(app, args)
    assert result.exit_code == 0, result.exception
    assert "not yet registered" in result.output
    assert len(calls) == 1
    receipt = json.loads((git_repo / ".git/connect-eagle/receipt.json").read_text())
    assert receipt["url"].endswith("/issues/1")
    assert (git_repo / ".git/config").read_bytes() == config_before
    assert (git_repo / ".connect-eagle.yml").read_bytes() == metadata_before


def test_issue_cli_requires_destination_and_rejects_both_routes(git_repo):
    runner = CliRunner()
    runner.invoke(app, ["init", "--path", str(git_repo), "--non-interactive",
                       "--mission", "TIR", "--description", "Satellite tools."])
    result = runner.invoke(app, ["submit", "--path", str(git_repo), "--issue"])
    assert result.exit_code != 0
    assert "requires --registry" in str(result.exception)
    result = runner.invoke(app, ["submit", "--path", str(git_repo), "--issue", "--push"])
    assert result.exit_code != 0
    assert "Choose either" in str(result.exception)
