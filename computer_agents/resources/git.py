"""Git resource manager.

Handles git operations on cloud workspaces including
status, staging, commit, branch, and push.
"""

from __future__ import annotations

from typing import Any

from .._api_client import ApiClient
from ..types import GitCommitResult, GitPushResult


class GitResource:
    """Git operations on ACP computers.

    Example::

        status = client.git.get_status("env_xxx")
        client.git.commit("env_xxx", message="Add feature")
        client.git.push("env_xxx")
    """

    def __init__(self, client: ApiClient) -> None:
        self._client = client

    def get_status(self, environment_id: str, *, path: str | None = None) -> dict[str, Any]:
        query = {"path": path} if path is not None else None
        return self._client.get(f"/environments/{environment_id}/git/status", query=query)

    def stage(
        self,
        environment_id: str,
        *,
        files: list[str] | None = None,
        path: str | None = None,
        all: bool | None = None,
    ) -> dict[str, Any]:
        body: dict[str, Any] = {}
        if files is not None:
            body["files"] = files
        if path is not None:
            body["path"] = path
        if all is not None:
            body["all"] = all
        return self._client.post(f"/environments/{environment_id}/git/stage", body)

    def unstage(
        self,
        environment_id: str,
        *,
        files: list[str] | None = None,
        path: str | None = None,
        all: bool | None = None,
    ) -> dict[str, Any]:
        body: dict[str, Any] = {}
        if files is not None:
            body["files"] = files
        if path is not None:
            body["path"] = path
        if all is not None:
            body["all"] = all
        return self._client.post(f"/environments/{environment_id}/git/unstage", body)

    def commit(
        self,
        environment_id: str,
        message: str,
        *,
        path: str | None = None,
        files: list[str] | None = None,
    ) -> GitCommitResult:
        """Create a git commit."""
        if files:
            self.stage(environment_id, files=files, path=path)
        body: dict[str, Any] = {"message": message}
        if path is not None:
            body["path"] = path
        return self._client.post(f"/environments/{environment_id}/git/commit", body)

    def push(
        self,
        environment_id: str,
        *,
        path: str | None = None,
        branch: str | None = None,
    ) -> GitPushResult:
        """Push commits to remote."""
        body: dict[str, Any] = {}
        if path is not None:
            body["path"] = path
        if branch is not None:
            body["branch"] = branch
        return self._client.post(f"/environments/{environment_id}/git/push", body)

    def create_branch(self, environment_id: str, name: str, *, path: str | None = None) -> dict[str, Any]:
        body: dict[str, Any] = {"name": name}
        if path is not None:
            body["path"] = path
        return self._client.post(f"/environments/{environment_id}/git/branch", body)

    def switch_branch(self, environment_id: str, name: str, *, path: str | None = None) -> dict[str, Any]:
        body: dict[str, Any] = {"name": name}
        if path is not None:
            body["path"] = path
        return self._client.put(f"/environments/{environment_id}/git/branch", body)

    def list_branches(self, environment_id: str, *, path: str | None = None) -> dict[str, Any]:
        query = {"path": path} if path is not None else None
        return self._client.get(f"/environments/{environment_id}/git/branches", query=query)

    def list_commits(
        self,
        environment_id: str,
        *,
        path: str | None = None,
        limit: int | None = None,
    ) -> dict[str, Any]:
        query: dict[str, Any] = {}
        if path is not None:
            query["path"] = path
        if limit is not None:
            query["limit"] = limit
        return self._client.get(f"/environments/{environment_id}/git/commits", query=query or None)

    def prepare_github(
        self,
        environment_id: str,
        *,
        repo_full_name: str,
        branch: str | None = None,
        project_id: str | None = None,
    ) -> dict[str, Any]:
        body: dict[str, Any] = {"repoFullName": repo_full_name}
        if branch is not None:
            body["branch"] = branch
        if project_id is not None:
            body["projectId"] = project_id
        return self._client.post(f"/environments/{environment_id}/github/prepare", body)

    def clone(
        self,
        environment_id: str,
        *,
        repo_url: str,
        branch: str | None = None,
        target_path: str | None = None,
        token: str | None = None,
    ) -> dict[str, Any]:
        body: dict[str, Any] = {"repoUrl": repo_url}
        if branch is not None:
            body["branch"] = branch
        if target_path is not None:
            body["targetPath"] = target_path
        if token is not None:
            body["token"] = token
        return self._client.post(f"/environments/{environment_id}/git/clone", body)
