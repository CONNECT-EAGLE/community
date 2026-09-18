import subprocess
from pathlib import Path

import pytest
from typer.testing import CliRunner

from connect_eagle.cli import app
from connect_eagle.metadata import load
from connect_eagle.repository import EagleError, Repository, public_url

runner = CliRunner()


def test_version_without_subcommand():
    result = runner.invoke(app, ["--version"])
    assert result.exit_code == 0
    assert "0.1.0" in result.output


def test_main_reports_errors_without_traceback(tmp_path):
    import sys

    result = subprocess.run(
        [sys.executable, "-m", "connect_eagle.cli", "doctor", "--path", str(tmp_path)],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 1
    assert "not a Git working tree" in result.stderr
    assert "Traceback" not in result.stderr


def invoke(repo: Path, *args: str):
    return runner.invoke(app, [args[0], "--path", str(repo), *args[1:]])


def initialize(repo: Path, *args: str):
    return invoke(
        repo,
        "init",
        "--non-interactive",
        "--mission",
        "both",
        "--description",
        "Compare satellite observations.",
        *args,
    )


def test_full_offline_loop_preserves_git(git_repo):
    before = (git_repo / ".git/config").read_bytes()
    assert initialize(git_repo).exit_code == 0
    assert (git_repo / ".git/config").read_bytes() == before
    assert (
        load(git_repo / ".connect-eagle.yml")["repository"]
        == "https://github.com/example/forest-tools"
    )
    assert "Unknown (offline" in invoke(git_repo, "status").output
    result = invoke(git_repo, "doctor")
    assert result.exit_code == 0, result.output
    assert "3 warning(s)" in result.output
    assert invoke(git_repo, "doctor", "--strict").exit_code == 1
    assert invoke(git_repo, "submit", "--dry-run").exit_code == 0
    assert not (git_repo / ".git/connect-eagle").exists()
    assert invoke(git_repo, "submit").exit_code == 0
    assert (git_repo / ".git/connect-eagle/submissions/forest-tools/forest-tools.yml").exists()
    assert (git_repo / ".git/config").read_bytes() == before


def test_existing_metadata_never_overwritten(git_repo):
    assert initialize(git_repo).exit_code == 0
    before = (git_repo / ".connect-eagle.yml").read_bytes()
    assert initialize(git_repo).exit_code != 0
    assert (git_repo / ".connect-eagle.yml").read_bytes() == before


def test_discovery_from_subdirectory_and_worktree(git_repo, tmp_path):
    (git_repo / "README.md").write_text("# Forest\nResearch software.\n")
    subprocess.run(["git", "-C", str(git_repo), "add", "README.md"], check=True)
    subprocess.run(
        ["git", "-C", str(git_repo), "commit", "-m", "init"], check=True, capture_output=True
    )
    sub = git_repo / "src"
    sub.mkdir()
    assert initialize(sub).exit_code == 0
    assert (git_repo / ".connect-eagle.yml").exists()
    worktree = tmp_path.parent / (tmp_path.name + "-worktree")
    subprocess.run(
        ["git", "-C", str(git_repo), "worktree", "add", "-b", "testing", str(worktree)],
        check=True,
        capture_output=True,
    )
    assert initialize(worktree).exit_code == 0
    assert invoke(worktree, "submit").exit_code == 0
    assert (Repository.discover(worktree).git_dir / "connect-eagle").exists()


@pytest.mark.parametrize(
    "file,content,name,description",
    [
        (
            "pyproject.toml",
            '[project]\nname="forest-python"\ndescription="Python forest tools"',
            "forest-python",
            "Python forest tools",
        ),
        (
            "package.json",
            '{"name":"forest-js","description":"JS forest tools"}',
            "forest-js",
            "JS forest tools",
        ),
        ("DESCRIPTION", "Package: forestR\nTitle: R forest tools", "forestR", "R forest tools"),
    ],
)
def test_language_inference(git_repo, file, content, name, description):
    (git_repo / file).write_text(content)
    result = invoke(git_repo, "init", "--non-interactive", "--mission", "TIR")
    assert result.exit_code == 0, result.exception
    data = load(git_repo / ".connect-eagle.yml")
    assert data["project"]["name"] == name
    assert data["project"]["description"] == description


def test_multiple_remotes_choose_origin_and_allow_override(git_repo):
    subprocess.run(
        [
            "git",
            "-C",
            str(git_repo),
            "remote",
            "add",
            "upstream",
            "https://github.com/upstream/forest-tools.git",
        ],
        check=True,
    )
    assert Repository.discover(git_repo).choose_url() == "https://github.com/example/forest-tools"
    assert initialize(git_repo, "--remote", "upstream").exit_code == 0
    assert load(git_repo / ".connect-eagle.yml")["repository"].startswith(
        "https://github.com/upstream/"
    )


def test_ambiguous_remotes_require_choice(git_repo):
    subprocess.run(["git", "-C", str(git_repo), "remote", "rename", "origin", "one"], check=True)
    subprocess.run(
        ["git", "-C", str(git_repo), "remote", "add", "two", "https://gitlab.com/lab/two"],
        check=True,
    )
    assert initialize(git_repo).exit_code != 0
    assert initialize(git_repo, "--remote", "one").exit_code == 0


@pytest.mark.parametrize(
    "remote,expected",
    [
        ("git@github.com:owner/repo.git", "https://github.com/owner/repo"),
        (
            "ssh://git@gitlab.com:2222/group/subgroup/repo.git",
            "https://gitlab.com/group/subgroup/repo",
        ),
        (
            "https://token:secret@github.com/owner/repo.git?token=secret#frag",
            "https://github.com/owner/repo",
        ),
        ("https://example.org:8443/lab/repo.git", "https://example.org:8443/lab/repo"),
        ("C:\\code\\repo", None),
        ("/tmp/local", None),
        ("file:///tmp/repo", None),
    ],
)
def test_remote_normalization(remote, expected):
    assert public_url(remote) == expected


def test_non_github(git_repo):
    assert initialize(git_repo, "--repository", "https://gitlab.com/lab/tools").exit_code == 0
    assert load(git_repo / ".connect-eagle.yml")["repository"] == "https://gitlab.com/lab/tools"
    assert invoke(git_repo, "submit").exit_code == 0


def test_detached_and_merge_in_progress_block_submit(git_repo):
    assert initialize(git_repo).exit_code == 0
    subprocess.run(["git", "-C", str(git_repo), "add", ".connect-eagle.yml"], check=True)
    subprocess.run(
        ["git", "-C", str(git_repo), "commit", "-m", "init"], check=True, capture_output=True
    )
    subprocess.run(
        ["git", "-C", str(git_repo), "checkout", "--detach"], check=True, capture_output=True
    )
    assert "Detached HEAD" in invoke(git_repo, "doctor").output
    assert invoke(git_repo, "submit").exit_code != 0
    subprocess.run(
        ["git", "-C", str(git_repo), "checkout", "main"], check=True, capture_output=True
    )
    (git_repo / ".git/MERGE_HEAD").write_text("abc")
    assert invoke(git_repo, "submit").exit_code != 0


def test_no_git_clean_error(tmp_path):
    with pytest.raises(EagleError, match="not a Git"):
        Repository.discover(tmp_path)


def test_noninteractive_missing_information(git_repo):
    result = invoke(git_repo, "init", "--non-interactive")
    assert result.exit_code != 0
    assert not (git_repo / ".connect-eagle.yml").exists()


def test_conflicting_metadata(git_repo):
    (git_repo / ".connect-eagle.yaml").write_text("schema: 1")
    assert initialize(git_repo).exit_code != 0
    assert "Conflicting" in invoke(git_repo, "doctor").output


def test_missing_gh_is_actionable(git_repo, monkeypatch):
    assert initialize(git_repo).exit_code == 0
    from connect_eagle import github

    def missing(*args, **kwargs):
        raise EagleError("Install gh and ensure it is on PATH.")

    monkeypatch.setattr(github, "command", missing)
    result = invoke(git_repo, "submit", "--push", "--registry", "lab/project-registry")
    assert isinstance(result.exception, EagleError)
    assert "Install gh" in str(result.exception)
