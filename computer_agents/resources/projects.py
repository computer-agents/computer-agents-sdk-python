"""Projects resource manager.

Handles project-related API operations.
Each API key is bound to exactly one project.
"""

from __future__ import annotations

from typing import Any

from .._api_client import ApiClient
from ..types import FileEntry, Project, ProjectDetailResult, ProjectListResult


_FIELD_ALIASES = {
    "default_environment_id": "defaultEnvironmentId",
    "environment_ids": "environmentIds",
}


def _api_body(params: dict[str, Any]) -> dict[str, Any]:
    return {
        _FIELD_ALIASES.get(key, key): value
        for key, value in params.items()
        if value is not None
    }


class ProjectsResource:
    """Project access (internal).

    Each API key is bound to exactly one project.
    Use ``client.files`` for file operations instead.
    """

    def __init__(self, client: ApiClient) -> None:
        self._client = client

    def list(
        self,
        *,
        type: str | None = None,
        q: str | None = None,
        limit: int | None = None,
    ) -> ProjectListResult:
        """List planning projects for the authenticated user."""
        query = {
            key: value
            for key, value in {"type": type, "q": q, "limit": limit}.items()
            if value is not None
        }
        resp = self._client.get("/projects", query=query or None)
        data = resp.get("data", [])
        return {
            "data": data,
            "hasMore": resp.get("has_more", False),
            "total": resp.get("total_count", len(data)),
        }

    def create(self, name: str, **params: Any) -> Project:
        """Create a planning project."""
        resp = self._client.post("/projects", {"name": name, **_api_body(params)})
        return resp["project"]

    def get_by_id(self, project_id: str) -> ProjectDetailResult:
        """Get a planning project by ID."""
        return self._client.get(f"/projects/{project_id}")

    def update_by_id(self, project_id: str, **params: Any) -> Project:
        """Update a planning project by ID."""
        resp = self._client.patch(f"/projects/{project_id}", _api_body(params))
        return resp["project"]

    def delete_by_id(self, project_id: str) -> dict[str, Any]:
        """Delete a planning project by ID."""
        return self._client.delete(f"/projects/{project_id}")

    def list_schedules(
        self,
        project_id: str,
        *,
        range_start: str | None = None,
        range_end: str | None = None,
    ) -> dict[str, Any]:
        """List schedules attached to a planning project."""
        query = {
            key: value
            for key, value in {
                "rangeStart": range_start,
                "rangeEnd": range_end,
            }.items()
            if value is not None
        }
        resp = self._client.get(f"/projects/{project_id}/schedules", query=query or None)
        data = resp.get("data", [])
        return {
            "data": data,
            "hasMore": resp.get("has_more", False),
            "total": resp.get("total_count", len(data)),
        }

    def get(self) -> Project:
        """Get the current project (bound to this API key)."""
        resp = self._client.get("/project")
        return resp["project"]

    def update(self, **params: Any) -> Project:
        """Update the current project."""
        body: dict[str, Any] = {}
        key_map = {
            "name": "name",
            "description": "description",
            "metadata": "metadata",
            "tags": "tags",
        }
        for py_key, api_key in key_map.items():
            if py_key in params:
                body[api_key] = params[py_key]
        resp = self._client.patch("/project", body)
        return resp["project"]

    def sync(
        self,
        *,
        added: list[str] | None = None,
        modified: list[str] | None = None,
        deleted: list[str] | None = None,
    ) -> dict[str, Any]:
        """Sync project with cloud storage."""
        changes: dict[str, list[str]] = {}
        if added is not None:
            changes["added"] = added
        if modified is not None:
            changes["modified"] = modified
        if deleted is not None:
            changes["deleted"] = deleted
        return self._client.post("/project/sync", {"changes": changes or None})
