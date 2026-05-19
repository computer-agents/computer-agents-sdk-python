"""Tasks resource manager.

Handles planning tasks, comments, sprints, releases, workspace board payloads,
and task-to-thread execution.
"""

from __future__ import annotations

from typing import Any

from .._api_client import ApiClient
from ..types import (
    Task,
    TaskComment,
    TaskCommentListResult,
    TaskDetailResult,
    TaskListResult,
    TaskRelease,
    TaskReleaseDetailResult,
    TaskReleaseListResult,
    TaskRunThreadResult,
    TaskSprint,
    TaskSprintDetailResult,
    TaskSprintListResult,
    TaskStartThreadResult,
    TaskWorkspaceResult,
)


def _list_result(resp: dict[str, Any]) -> dict[str, Any]:
    data = resp.get("data", [])
    return {
        "data": data,
        "hasMore": resp.get("has_more", False),
        "total": resp.get("total_count", len(data)),
    }


def _query_from_kwargs(kwargs: dict[str, Any]) -> dict[str, Any] | None:
    return {key: value for key, value in kwargs.items() if value is not None} or None


_FIELD_ALIASES = {
    "agent_id": "agentId",
    "assignee_agent_id": "assigneeAgentId",
    "author_agent_id": "authorAgentId",
    "author_name": "authorName",
    "author_type": "authorType",
    "completed_at": "completedAt",
    "dependency_ids": "dependencyIds",
    "due_at": "dueAt",
    "end_at": "endAt",
    "environment_id": "environmentId",
    "last_started_thread_id": "lastStartedThreadId",
    "linked_thread_ids": "linkedThreadIds",
    "move_to_in_progress": "moveToInProgress",
    "parent_task_id": "parentTaskId",
    "project_id": "projectId",
    "release_id": "releaseId",
    "scheduled_end_at": "scheduledEndAt",
    "scheduled_start_at": "scheduledStartAt",
    "sort_order": "sortOrder",
    "source_thread_id": "sourceThreadId",
    "sprint_id": "sprintId",
    "start_at": "startAt",
    "task_type": "taskType",
    "thread_id": "threadId",
}


def _api_body(params: dict[str, Any]) -> dict[str, Any]:
    return {
        _FIELD_ALIASES.get(key, key): value
        for key, value in params.items()
        if value is not None
    }


class TasksResource:
    """Task planning and task-thread execution."""

    def __init__(self, client: ApiClient) -> None:
        self._client = client

    def list(
        self,
        *,
        project_id: str | None = None,
        release_id: str | None = None,
        sprint_id: str | None = None,
        status: str | None = None,
        assignee_agent_id: str | None = None,
        q: str | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> TaskListResult:
        """List tasks across projects."""
        resp = self._client.get(
            "/tasks",
            query=_query_from_kwargs({
                "projectId": project_id,
                "releaseId": release_id,
                "sprintId": sprint_id,
                "status": status,
                "assigneeAgentId": assignee_agent_id,
                "q": q,
                "limit": limit,
                "offset": offset,
            }),
        )
        return _list_result(resp)

    def create(self, title: str, **params: Any) -> Task:
        """Create a task."""
        body = {"title": title, **_api_body(params)}
        resp = self._client.post("/tasks", body)
        return resp["task"]

    def get(self, task_id: str) -> TaskDetailResult:
        """Get a task with details, linked threads, and comments."""
        return self._client.get(f"/tasks/{task_id}")

    def update(self, task_id: str, **params: Any) -> Task:
        """Update a task."""
        resp = self._client.patch(f"/tasks/{task_id}", _api_body(params))
        return resp["task"]

    def delete(self, task_id: str) -> dict[str, Any]:
        """Delete a task."""
        return self._client.delete(f"/tasks/{task_id}")

    def workspace(
        self,
        *,
        project_id: str | None = None,
        q: str | None = None,
        range_start: str | None = None,
        range_end: str | None = None,
    ) -> TaskWorkspaceResult:
        """Build the board-ready task workspace payload."""
        return self._client.get(
            "/tasks/workspace",
            query=_query_from_kwargs({
                "projectId": project_id,
                "q": q,
                "rangeStart": range_start,
                "rangeEnd": range_end,
            }),
        )

    def list_comments(
        self,
        task_id: str,
        *,
        author_type: str | None = None,
        author_agent_id: str | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> TaskCommentListResult:
        """List task comments."""
        resp = self._client.get(
            f"/tasks/{task_id}/comments",
            query=_query_from_kwargs({
                "authorType": author_type,
                "authorAgentId": author_agent_id,
                "limit": limit,
                "offset": offset,
            }),
        )
        return _list_result(resp)

    def create_comment(self, task_id: str, **params: Any) -> TaskComment:
        """Create a task comment."""
        resp = self._client.post(f"/tasks/{task_id}/comments", _api_body(params))
        return resp["comment"]

    def start_thread(self, task_id: str, **params: Any) -> TaskStartThreadResult:
        """Create and link a new thread for a task."""
        return self._client.post(f"/tasks/{task_id}/start-thread", _api_body(params) or None)

    def run_thread(self, task_id: str, **params: Any) -> TaskRunThreadResult:
        """Create, link, and synchronously execute a new thread for a task."""
        return self._client.post(f"/tasks/{task_id}/run-thread", _api_body(params) or None)

    def list_sprints(
        self,
        *,
        project_id: str | None = None,
        status: str | None = None,
        q: str | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> TaskSprintListResult:
        """List sprints."""
        resp = self._client.get(
            "/tasks/sprints",
            query=_query_from_kwargs({
                "projectId": project_id,
                "status": status,
                "q": q,
                "limit": limit,
                "offset": offset,
            }),
        )
        return _list_result(resp)

    def create_sprint(self, name: str, **params: Any) -> TaskSprint:
        """Create a sprint."""
        resp = self._client.post("/tasks/sprints", {"name": name, **_api_body(params)})
        return resp["sprint"]

    def get_sprint(self, sprint_id: str) -> TaskSprintDetailResult:
        """Get a sprint and its tasks."""
        return self._client.get(f"/tasks/sprints/{sprint_id}")

    def update_sprint(self, sprint_id: str, **params: Any) -> TaskSprint:
        """Update a sprint."""
        resp = self._client.patch(f"/tasks/sprints/{sprint_id}", _api_body(params))
        return resp["sprint"]

    def delete_sprint(self, sprint_id: str) -> dict[str, Any]:
        """Delete a sprint."""
        return self._client.delete(f"/tasks/sprints/{sprint_id}")

    def list_releases(
        self,
        *,
        project_id: str | None = None,
        q: str | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> TaskReleaseListResult:
        """List releases."""
        resp = self._client.get(
            "/tasks/releases",
            query=_query_from_kwargs({
                "projectId": project_id,
                "q": q,
                "limit": limit,
                "offset": offset,
            }),
        )
        return _list_result(resp)

    def create_release(self, project_id: str, name: str, **params: Any) -> TaskRelease:
        """Create a release."""
        resp = self._client.post(
            "/tasks/releases",
            {"projectId": project_id, "name": name, **_api_body(params)},
        )
        return resp["release"]

    def get_release(self, release_id: str) -> TaskReleaseDetailResult:
        """Get a release and its tasks."""
        return self._client.get(f"/tasks/releases/{release_id}")

    def update_release(self, release_id: str, **params: Any) -> TaskRelease:
        """Update a release."""
        resp = self._client.patch(f"/tasks/releases/{release_id}", _api_body(params))
        return resp["release"]

    def delete_release(self, release_id: str) -> dict[str, Any]:
        """Delete a release."""
        return self._client.delete(f"/tasks/releases/{release_id}")
