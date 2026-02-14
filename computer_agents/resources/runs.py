"""Runs resource manager.

Handles execution tracking including CRUD operations,
logs retrieval, and file diffs.
"""

from __future__ import annotations

from typing import Any

from .._api_client import ApiClient
from ..types import Run, RunDiff, RunLogEntry


class RunsResource:
    """Run tracking (internal).

    Used for tracking individual execution runs within threads.
    """

    def __init__(self, client: ApiClient) -> None:
        self._client = client

    def create(self, **params: Any) -> Run:
        """Create a new run."""
        body: dict[str, Any] = {}
        key_map = {
            "agent_id": "agentId",
            "agent_name": "agentName",
            "name": "name",
            "task": "task",
            "prompt": "prompt",
            "title": "title",
            "workspace_name": "workspaceName",
            "workspace_id": "workspaceId",
            "context_id": "contextId",
            "environment_id": "environmentId",
            "environment_name": "environmentName",
            "attachments": "attachments",
            "metadata": "metadata",
            "thread_id": "threadId",
        }
        for py_key, api_key in key_map.items():
            if py_key in params:
                body[api_key] = params[py_key]
        resp = self._client.post("/runs", body)
        return resp["run"]

    def list(
        self,
        *,
        thread_id: str | None = None,
        status: str | None = None,
        since: str | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> dict[str, Any]:
        """List runs."""
        query: dict[str, Any] = {}
        if thread_id is not None:
            query["threadId"] = thread_id
        if status is not None:
            query["status"] = status
        if since is not None:
            query["since"] = since
        if limit is not None:
            query["limit"] = limit
        if offset is not None:
            query["offset"] = offset
        return self._client.get("/runs", query=query or None)

    def get(self, run_id: str) -> Run:
        """Get a run by ID."""
        resp = self._client.get(f"/runs/{run_id}")
        return resp["run"]

    def update(self, run_id: str, **params: Any) -> Run:
        """Update a run."""
        body: dict[str, Any] = {}
        key_map = {
            "name": "name",
            "status": "status",
            "duration": "duration",
            "cost": "cost",
            "logs": "logs",
            "metadata": "metadata",
            "token_usage": "tokenUsage",
            "title": "title",
        }
        for py_key, api_key in key_map.items():
            if py_key in params:
                body[api_key] = params[py_key]
        resp = self._client.patch(f"/runs/{run_id}", body)
        return resp["run"]

    def delete(self, run_id: str) -> None:
        """Delete a run."""
        self._client.delete(f"/runs/{run_id}")

    def get_logs(
        self,
        run_id: str,
        *,
        level: str | None = None,
        format: str | None = None,
    ) -> list[RunLogEntry]:
        """Get logs for a run."""
        query: dict[str, Any] = {}
        if level is not None:
            query["level"] = level
        if format is not None:
            query["format"] = format
        resp = self._client.get(f"/runs/{run_id}/logs", query=query or None)
        return resp["logs"]

    def append_log(
        self,
        run_id: str,
        level: str,
        message: str,
        *,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Append a log entry to a run."""
        body: dict[str, Any] = {"level": level, "message": message}
        if metadata is not None:
            body["metadata"] = metadata
        self._client.post(f"/runs/{run_id}/logs", body)

    def get_diffs(self, run_id: str) -> list[RunDiff]:
        """Get file diffs for a run."""
        resp = self._client.get(f"/threads/{run_id}/diffs")
        return resp["diffs"]
