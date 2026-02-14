"""Git resource manager.

Handles git operations on cloud workspaces including
diff, commit, and push.
"""

from __future__ import annotations

from typing import Any

from .._api_client import ApiClient
from ..types import GitCommitResult, GitDiffResult, GitPushResult


class GitResource:
    """Git operations on cloud workspaces.

    Example::

        diff = client.git.diff("env_xxx")
        client.git.commit("env_xxx", message="Add feature")
        client.git.push("env_xxx")
    """

    def __init__(self, client: ApiClient) -> None:
        self._client = client

    def diff(self, workspace_id: str) -> GitDiffResult:
        """Get uncommitted changes in a workspace."""
        return self._client.get(f"/git/{workspace_id}/diff")

    def commit(
        self,
        workspace_id: str,
        message: str,
        *,
        author: dict[str, str] | None = None,
        files: list[str] | None = None,
    ) -> GitCommitResult:
        """Create a git commit."""
        body: dict[str, Any] = {"message": message}
        if author is not None:
            body["author"] = author
        if files is not None:
            body["files"] = files
        return self._client.post(f"/git/{workspace_id}/commit", body)

    def push(
        self,
        workspace_id: str,
        *,
        remote: str | None = None,
        branch: str | None = None,
        force: bool | None = None,
    ) -> GitPushResult:
        """Push commits to remote."""
        body: dict[str, Any] = {}
        if remote is not None:
            body["remote"] = remote
        if branch is not None:
            body["branch"] = branch
        if force is not None:
            body["force"] = force
        return self._client.post(f"/git/{workspace_id}/push", body)

    def get_commit_diff(
        self, workspace_id: str, commit_sha: str
    ) -> GitDiffResult:
        """Get diff for a specific commit."""
        return self._client.get(f"/git/{workspace_id}/commits/{commit_sha}/diff")
