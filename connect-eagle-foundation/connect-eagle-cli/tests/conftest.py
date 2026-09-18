import subprocess
from pathlib import Path

import pytest


@pytest.fixture
def git_repo(tmp_path: Path) -> Path:
    subprocess.run(["git", "init", "-b", "main", str(tmp_path)], check=True, capture_output=True)
    subprocess.run(["git", "-C", str(tmp_path), "config", "user.name", "Test User"], check=True)
    subprocess.run(
        ["git", "-C", str(tmp_path), "config", "user.email", "test@example.org"], check=True
    )
    subprocess.run(
        [
            "git",
            "-C",
            str(tmp_path),
            "remote",
            "add",
            "origin",
            "git@github.com:example/forest-tools.git",
        ],
        check=True,
    )
    return tmp_path


@pytest.fixture
def record() -> dict:
    return {
        "schema": 1,
        "project": {
            "name": "Forest Tools",
            "slug": "forest-tools",
            "description": "Forest observations.",
        },
        "eagle": {"mission": ["VSWIR", "TIR"], "topics": ["ecology"]},
        "project_type": "software",
        "status": "active",
        "collaboration": {"open": True, "looking_for": ["researcher"]},
        "repository": "https://github.com/example/forest-tools",
    }
