"""Git stage + commit + branch + push for the config-repo working tree."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import git


def commit_and_push(
    working_path: str,
    branch: str,
    commit_message: str,
    base_branch: str = "main",
    push: bool = True,
) -> dict[str, Any]:
    repo_path = Path(working_path)
    repo = git.Repo(repo_path)

    if repo.is_dirty(untracked_files=True) is False:
        return {"committed": False, "reason": "no changes"}

    repo.git.fetch("origin", base_branch)

    if branch in repo.heads:
        repo.heads[branch].checkout()
    else:
        repo.git.checkout("-b", branch, f"origin/{base_branch}")

    repo.git.add(A=True)
    commit = repo.index.commit(commit_message)

    if push:
        repo.git.push("--set-upstream", "origin", branch)

    return {
        "committed": True,
        "branch": branch,
        "sha": commit.hexsha,
        "summary": commit.summary,
    }
