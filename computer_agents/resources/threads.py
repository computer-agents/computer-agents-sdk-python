"""Threads resource manager.

Handles conversation threads including CRUD operations,
message execution with SSE streaming, and conversation history.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Iterator, Optional

from .._api_client import ApiClient
from ..types import (
    ResearchSession,
    SearchThreadsResponse,
    Thread,
    ThreadFeedbackReport,
    ThreadFeedbackSummary,
    ThreadLogEntry,
    ThreadPermissionDecisionResponse,
    ThreadPermissionRequest,
)


def _query(params: dict[str, Any], **values: Any) -> dict[str, Any] | None:
    query = dict(params)
    query.update({key: value for key, value in values.items() if value is not None})
    return query or None


@dataclass
class SendMessageResult:
    """Result from sending a message to a thread."""

    content: str
    """The final response content."""

    events: list[dict[str, Any]] = field(default_factory=list)
    """All SSE events received during streaming."""

    run: Optional[dict[str, Any]] = None
    """Run details if available."""

    queued_in_batch: bool = False
    """Whether execution was durably deferred to Batches."""

    batch_job_id: Optional[str] = None
    """Durable Batch job identity when execution was deferred."""

    admission_reason: Optional[str] = None
    """Stable runtime admission reason when execution was deferred."""


class ThreadsResource:
    """Thread (conversation) management.

    Create threads for multi-turn conversations with agents.
    Use :meth:`send_message` for SSE streaming execution.

    Example::

        thread = client.threads.create(environment_id="env_xxx")
        result = client.threads.send_message(
            thread["id"],
            content="Fix the TypeScript errors",
            on_event=lambda e: print(e),
        )
    """

    def __init__(self, client: ApiClient) -> None:
        self._client = client

    def create(
        self,
        environment_id: str | None = None,
        *,
        project_id: str | None = None,
        agent_id: str | None = None,
        title: str | None = None,
        app_id: str | None = None,
        messages: list[dict[str, Any]] | None = None,
        content: str | None = None,
        task: str | None = None,
        schedule: dict[str, Any] | None = None,
        attachments: list[dict[str, Any]] | None = None,
        github_repo: dict[str, Any] | None = None,
        metadata: dict[str, Any] | None = None,
        message_metadata: dict[str, Any] | None = None,
        enabled_skills: list[str] | None = None,
        reasoning_effort: str | None = None,
        env_vars: dict[str, str] | None = None,
        idempotency_key: str | None = None,
        queue_when_capacity_unavailable: bool | None = None,
        knowledge_context: dict[str, Any] | None = None,
    ) -> Thread:
        """Create a thread using a non-streaming JSON response."""
        response = self.create_with_response(
            environment_id,
            project_id=project_id,
            agent_id=agent_id,
            title=title,
            app_id=app_id,
            messages=messages,
            content=content,
            task=task,
            schedule=schedule,
            attachments=attachments,
            github_repo=github_repo,
            metadata=metadata,
            message_metadata=message_metadata,
            enabled_skills=enabled_skills,
            reasoning_effort=reasoning_effort,
            env_vars=env_vars,
            idempotency_key=idempotency_key,
            queue_when_capacity_unavailable=queue_when_capacity_unavailable,
            knowledge_context=knowledge_context,
        )
        thread = dict(response["thread"])
        for key in ("queuedInBatch", "batchJobId", "admissionReason"):
            if key in response:
                thread[key] = response[key]
        return thread  # type: ignore[return-value]

    def create_with_response(
        self,
        environment_id: str | None = None,
        **params: Any,
    ) -> dict[str, Any]:
        """Create a thread and preserve execution, schedule, and Batch metadata."""
        body = self._create_body(environment_id, params)
        if body.get("messages") or body.get("content") or body.get("task"):
            body["stream"] = False
        idempotency_key = str(params.get("idempotency_key") or "").strip()
        if idempotency_key:
            return self._client.request(
                "POST",
                "/threads",
                body=body,
                headers={"Idempotency-Key": idempotency_key},
            )
        return self._client.post("/threads", body)

    def create_stream(
        self,
        environment_id: str | None = None,
        *,
        timeout: float | None = None,
        **params: Any,
    ) -> Iterator[dict[str, Any]]:
        """Create and execute a thread, yielding its authenticated SSE events."""
        body = self._create_body(environment_id, params)
        body["stream"] = True
        idempotency_key = str(params.get("idempotency_key") or "").strip()
        return self._client.request_stream(
            "POST",
            "/threads",
            body=body,
            headers={"Idempotency-Key": idempotency_key} if idempotency_key else None,
            timeout=timeout or 600.0,
        )

    @staticmethod
    def _create_body(environment_id: str | None, params: dict[str, Any]) -> dict[str, Any]:
        body: dict[str, Any] = {}
        if environment_id is not None:
            body["environmentId"] = environment_id
        field_map = {
            "project_id": "projectId",
            "agent_id": "agentId",
            "title": "title",
            "app_id": "appId",
            "messages": "messages",
            "content": "content",
            "task": "task",
            "schedule": "schedule",
            "attachments": "attachments",
            "github_repo": "githubRepo",
            "metadata": "metadata",
            "message_metadata": "messageMetadata",
            "enabled_skills": "enabledSkills",
            "reasoning_effort": "reasoningEffort",
            "env_vars": "envVars",
            "queue_when_capacity_unavailable": "queueWhenCapacityUnavailable",
            "knowledge_context": "knowledgeContext",
        }
        for source, target in field_map.items():
            if params.get(source) is not None:
                body[target] = params[source]
        return body

    def list(
        self,
        *,
        project_id: str | None = None,
        environment_id: str | None = None,
        agent_id: str | None = None,
        app_id: str | None = None,
        schedule_id: str | None = None,
        status: str | None = None,
        created_after: str | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> dict[str, Any]:
        """List threads.

        Returns dict with ``data``, ``hasMore``, ``total`` keys.
        """
        query: dict[str, Any] = {}
        if project_id is not None:
            query["projectId"] = project_id
        if environment_id is not None:
            query["environmentId"] = environment_id
        if agent_id is not None:
            query["agentId"] = agent_id
        if app_id is not None:
            query["appId"] = app_id
        if schedule_id is not None:
            query["scheduleId"] = schedule_id
        if status is not None:
            query["status"] = status
        if created_after is not None:
            query["createdAfter"] = created_after
        if limit is not None:
            query["limit"] = limit
        if offset is not None:
            query["offset"] = offset
        resp = self._client.get("/threads", query=query)
        return {
            "data": resp["data"],
            "hasMore": resp.get("has_more", False),
            "total": resp.get("total_count", 0),
        }

    def get(self, thread_id: str) -> Thread:
        """Get a thread by ID with full message history."""
        resp = self._client.get(f"/threads/{thread_id}")
        return resp["thread"]

    def update(self, thread_id: str, **params: Any) -> Thread:
        """Update a thread.

        Args:
            thread_id: Thread ID.
            title: New title.
            status: New status.
        """
        body: dict[str, Any] = {}
        if "title" in params:
            body["title"] = params["title"]
        if "status" in params:
            body["status"] = params["status"]
        if "agent_id" in params:
            body["agentId"] = params["agent_id"]
        if "project_id" in params:
            body["projectId"] = params["project_id"]
        if "environment_id" in params:
            body["environmentId"] = params["environment_id"]
        if "app_id" in params:
            body["appId"] = params["app_id"]
        if "task" in params:
            body["task"] = params["task"]
        if "metadata" in params:
            body["metadata"] = params["metadata"]
        resp = self._client.patch(f"/threads/{thread_id}", body)
        return resp["thread"]

    def delete(self, thread_id: str) -> None:
        """Delete a thread (soft delete)."""
        self._client.delete(f"/threads/{thread_id}")

    def get_messages(
        self,
        thread_id: str,
        *,
        limit: int | None = None,
        offset: int | None = None,
        order: str | None = None,
        compact: bool | None = None,
    ) -> dict[str, Any]:
        """Get message history for a thread.

        Returns dict with ``data``, ``hasMore``, ``total`` keys.
        """
        resp = self._client.get(
            f"/threads/{thread_id}/messages",
            query={
                "limit": limit,
                "offset": offset,
                "order": order,
                "compact": compact,
            },
        )
        return {
            "data": resp["data"],
            "hasMore": resp.get("has_more", False),
            "total": resp.get("total_count", 0),
        }

    def send_message(
        self,
        thread_id: str,
        *,
        content: str,
        task: str | None = None,
        execution_content: str | None = None,
        mcp_servers: list[dict[str, Any]] | None = None,
        env_vars: dict[str, str] | None = None,
        attachments: list[dict[str, Any]] | None = None,
        github_repo: dict[str, Any] | None = None,
        quoted_selection: dict[str, str] | None = None,
        message_metadata: dict[str, Any] | None = None,
        research_mode_enabled: bool | None = None,
        truncate_at_message_index: int | None = None,
        enabled_skills: list[str] | None = None,
        edit_message_id: str | None = None,
        persist_file_changes: bool | None = None,
        reasoning_effort: str | None = None,
        queue_when_capacity_unavailable: bool | None = None,
        knowledge_context: dict[str, Any] | None = None,
        idempotency_key: str | None = None,
        on_event: Callable[[dict[str, Any]], None] | None = None,
        timeout: float | None = None,
    ) -> SendMessageResult:
        """Send a message to a thread and stream the response.

        Example::

            result = client.threads.send_message(
                "thread_456",
                content="Create a REST API with Flask",
                on_event=lambda event: print(event["type"]),
            )
            print("Response:", result.content)
        """
        body: dict[str, Any] = {"content": content}
        if task is not None:
            body["task"] = task
        if execution_content is not None:
            body["executionContent"] = execution_content
        if mcp_servers is not None:
            body["mcpServers"] = mcp_servers
        if env_vars is not None:
            body["envVars"] = env_vars
        if attachments is not None:
            body["attachments"] = attachments
        if github_repo is not None:
            body["githubRepo"] = github_repo
        if quoted_selection is not None:
            body["quotedSelection"] = quoted_selection
        if message_metadata is not None:
            body["messageMetadata"] = message_metadata
        if research_mode_enabled is not None:
            body["researchModeEnabled"] = research_mode_enabled
        if truncate_at_message_index is not None:
            body["truncateAtMessageIndex"] = truncate_at_message_index
        if enabled_skills is not None:
            body["enabledSkills"] = enabled_skills
        if edit_message_id is not None:
            body["editMessageId"] = edit_message_id
        if persist_file_changes is not None:
            body["persistFileChanges"] = persist_file_changes
        if reasoning_effort is not None:
            body["reasoningEffort"] = reasoning_effort
        if queue_when_capacity_unavailable is not None:
            body["queueWhenCapacityUnavailable"] = queue_when_capacity_unavailable
        if knowledge_context is not None:
            body["knowledgeContext"] = knowledge_context

        events: list[dict[str, Any]] = []
        final_content = ""
        run_details: dict[str, Any] | None = None
        queued_in_batch = False
        batch_job_id: str | None = None
        admission_reason: str | None = None

        for event in self._client.request_stream(
            "POST",
            f"/threads/{thread_id}/messages",
            body=body,
            headers={"Idempotency-Key": idempotency_key.strip()}
            if idempotency_key and idempotency_key.strip()
            else None,
            timeout=timeout or 600.0,
        ):
            events.append(event)

            if on_event is not None:
                on_event(event)

            event_type = event.get("type", "")
            if event_type == "response.completed":
                response_data = event.get("response", {})
                final_content = response_data.get("content", "")
            elif event_type == "stream.completed":
                run_details = event.get("run")
                queued_in_batch = event.get("queued") is True
                batch_job_id = str(event.get("batchJobId") or "").strip() or None
                admission_reason = str(event.get("admissionReason") or "").strip() or None
            elif event_type == "stream.error":
                raise Exception(
                    event.get("message") or event.get("error", "Stream error")
                )

        return SendMessageResult(
            content=final_content,
            events=events,
            run=run_details,
            queued_in_batch=queued_in_batch,
            batch_job_id=batch_job_id,
            admission_reason=admission_reason,
        )

    def copy(
        self,
        thread_id: str,
        *,
        title: str | None = None,
        truncate_at_message_index: int | None = None,
        environment_name: str | None = None,
        environment_target: str | None = None,
        environment_strategy: str | None = None,
        target_environment_id: str | None = None,
        file_copy_mode: str | None = None,
    ) -> Thread:
        """Copy a thread with all its conversation messages.

        Example::

            copy = client.threads.copy("thread_abc", title="My experiment v2")
        """
        resp = self.copy_with_response(
            thread_id,
            title=title,
            truncate_at_message_index=truncate_at_message_index,
            environment_name=environment_name,
            environment_target=environment_target,
            environment_strategy=environment_strategy,
            target_environment_id=target_environment_id,
            file_copy_mode=file_copy_mode,
        )
        return resp["thread"]

    def copy_with_response(self, thread_id: str, **params: Any) -> dict[str, Any]:
        """Copy or fork a thread and preserve environment/snapshot metadata."""
        aliases = {
            "truncate_at_message_index": "truncateAtMessageIndex",
            "environment_name": "environmentName",
            "environment_target": "environmentTarget",
            "environment_strategy": "environmentStrategy",
            "target_environment_id": "targetEnvironmentId",
            "file_copy_mode": "fileCopyMode",
        }
        body = {
            aliases.get(key, key): value
            for key, value in params.items()
            if value is not None
        }
        return self._client.post(f"/threads/{thread_id}/copy", body or None)

    def search(
        self,
        query: str,
        *,
        environment_id: str | None = None,
        status: str | None = None,
        limit: int | None = None,
        offset: int | None = None,
        include_messages: bool | None = None,
    ) -> SearchThreadsResponse:
        """Search threads by text query."""
        body: dict[str, Any] = {"query": query}
        if environment_id is not None:
            body["environmentId"] = environment_id
        if status is not None:
            body["status"] = status
        if limit is not None:
            body["limit"] = limit
        if offset is not None:
            body["offset"] = offset
        if include_messages is not None:
            body["includeMessages"] = include_messages
        return self._client.post("/threads/search", body)

    def get_logs(
        self,
        thread_id: str,
        *,
        compact: bool | None = None,
        include_conversation: bool | None = None,
    ) -> list[ThreadLogEntry]:
        """Get execution logs for a thread."""
        resp = self._client.get(
            f"/threads/{thread_id}/logs",
            query={
                "compact": compact,
                "includeConversation": include_conversation,
            },
        )
        return resp["logs"]

    def append_logs(self, thread_id: str, **params: Any) -> dict[str, Any]:
        """Append logs for a flow that bypasses the standard worker stream."""
        return self._client.post(f"/threads/{thread_id}/logs", params)

    def get_trace_clusters(
        self,
        thread_id: str,
        *,
        limit: int | None = None,
        step_limit: int | None = None,
        log_limit: int | None = None,
        observer: bool | None = None,
        **params: Any,
    ) -> dict[str, Any]:
        """Build decision-level trace clusters for a thread."""
        return self._client.get(
            f"/threads/{thread_id}/trace-clusters",
            query=_query(
                params,
                limit=limit,
                stepLimit=step_limit,
                logLimit=log_limit,
                observer=observer,
            ),
        )

    def ask_btw(
        self,
        thread_id: str,
        prompt: str,
        *,
        timeout: float | None = None,
    ) -> Iterator[dict[str, Any]]:
        """Stream a side-question answer while the main run continues."""
        return self._client.request_stream(
            "POST",
            f"/threads/{thread_id}/context/actions/btw/stream",
            body={"prompt": prompt},
            timeout=timeout,
        )

    def get_events(
        self,
        thread_id: str,
        *,
        after: str | None = None,
        before: str | None = None,
        cursor: str | None = None,
        limit: int | None = None,
        stream: bool | None = None,
        **params: Any,
    ) -> dict[str, Any]:
        """List the durable ordered event spine for a thread."""
        return self._client.get(
            f"/threads/{thread_id}/events",
            query=_query(
                params,
                after=after,
                before=before,
                cursor=cursor,
                limit=limit,
                stream=stream,
            ),
        )

    def stream_events(
        self,
        thread_id: str,
        *,
        after: str | None = None,
        before: str | None = None,
        cursor: str | None = None,
        limit: int | None = None,
        **params: Any,
    ) -> Iterator[dict[str, Any]]:
        """Open a replayable stream of canonical thread events."""
        return self._client.request_stream(
            "GET",
            f"/threads/{thread_id}/events",
            query=_query(
                params,
                after=after,
                before=before,
                cursor=cursor,
                limit=limit,
                stream=True,
            ),
        )

    def get_timeline(
        self,
        thread_id: str,
        *,
        after: str | None = None,
        before: str | None = None,
        cursor: str | None = None,
        limit: int | None = None,
        include_legacy: bool | None = None,
        **params: Any,
    ) -> dict[str, Any]:
        return self._client.get(
            f"/threads/{thread_id}/timeline",
            query=_query(
                params,
                after=after,
                before=before,
                cursor=cursor,
                limit=limit,
                includeLegacy=include_legacy,
            ),
        )

    def get_runs(
        self,
        thread_id: str,
        *,
        status: str | None = None,
        kind: str | None = None,
        limit: int | None = None,
        order: str | None = None,
        offset: int | None = None,
        include_legacy: bool | None = None,
        **params: Any,
    ) -> dict[str, Any]:
        return self._client.get(
            f"/threads/{thread_id}/runs",
            query=_query(
                params,
                status=status,
                kind=kind,
                limit=limit,
                order=order,
                offset=offset,
                includeLegacy=include_legacy,
            ),
        )

    def get_activity_groups(
        self,
        thread_id: str,
        *,
        run_id: str | None = None,
        status: str | None = None,
        after: str | None = None,
        before: str | None = None,
        cursor: str | None = None,
        limit: int | None = None,
        **params: Any,
    ) -> dict[str, Any]:
        return self._client.get(
            f"/threads/{thread_id}/activity-groups",
            query=_query(
                params,
                runId=run_id,
                status=status,
                after=after,
                before=before,
                cursor=cursor,
                limit=limit,
            ),
        )

    def classify_activity(self, thread_id: str, **params: Any) -> dict[str, Any]:
        return self._client.post(f"/threads/{thread_id}/activity/classify", params)

    def get_actions(
        self,
        thread_id: str,
        *,
        run_id: str | None = None,
        group_id: str | None = None,
        after: str | None = None,
        limit: int | None = None,
        include_legacy: bool | None = None,
        **params: Any,
    ) -> dict[str, Any]:
        return self._client.get(
            f"/threads/{thread_id}/actions",
            query=_query(
                params,
                runId=run_id,
                groupId=group_id,
                after=after,
                limit=limit,
                includeLegacy=include_legacy,
            ),
        )

    def send_activity_message(self, thread_id: str, **params: Any) -> dict[str, Any]:
        return self._client.post(f"/threads/{thread_id}/activity/messages", params)

    def steer_run(
        self,
        thread_id: str,
        run_id: str,
        **params: Any,
    ) -> dict[str, Any]:
        return self._client.post(
            f"/threads/{thread_id}/runs/{run_id}/steering",
            params,
        )

    def control_run(
        self,
        thread_id: str,
        run_id: str,
        *,
        action: str,
        **params: Any,
    ) -> dict[str, Any]:
        return self._client.post(
            f"/threads/{thread_id}/runs/{run_id}/control",
            {"action": action, **params},
        )

    def get_status(self, thread_id: str) -> dict[str, Any]:
        """Get execution status for a thread."""
        return self._client.get(f"/threads/{thread_id}/status")

    def list_steps(
        self,
        thread_id: str,
        *,
        limit: int | None = None,
        offset: int | None = None,
        compact: bool | None = None,
    ) -> list[dict[str, Any]]:
        query: dict[str, Any] = {}
        if limit is not None:
            query["limit"] = limit
        if offset is not None:
            query["offset"] = offset
        if compact is not None:
            query["compact"] = compact
        resp = self._client.get(f"/threads/{thread_id}/steps", query=query or None)
        return resp["data"]

    def list_step_files(
        self,
        thread_id: str,
        step_id: str,
        *,
        prefix: str | None = None,
    ) -> list[dict[str, Any]]:
        query = {"prefix": prefix} if prefix is not None else None
        resp = self._client.get(f"/threads/{thread_id}/steps/{step_id}/files", query=query)
        return resp["data"]

    def get_step_diff(
        self,
        thread_id: str,
        step_id: str,
        *,
        path: str | None = None,
    ) -> dict[str, Any]:
        query = {"path": path} if path is not None else None
        return self._client.get(f"/threads/{thread_id}/steps/{step_id}/diff", query=query)

    def get_step_file(self, thread_id: str, step_id: str, *, path: str) -> dict[str, Any]:
        return self._client.get(
            f"/threads/{thread_id}/steps/{step_id}/file",
            query={"path": path},
        )

    def download_step_file(self, thread_id: str, step_id: str, *, path: str) -> bytes:
        resp = self._client.request_raw(
            "GET",
            f"/threads/{thread_id}/steps/{step_id}/file/download",
            query={"path": path},
        )
        return resp.content

    def fork_from_step(self, thread_id: str, step_id: str, **params: Any) -> dict[str, Any]:
        return self._client.post(f"/threads/{thread_id}/steps/{step_id}/fork", params)

    def revert_to_step(self, thread_id: str, step_id: str, **params: Any) -> dict[str, Any]:
        return self._client.post(f"/threads/{thread_id}/steps/{step_id}/revert", params)

    def get_file_history(
        self,
        thread_id: str,
        *,
        path: str,
        limit: int | None = None,
        offset: int | None = None,
    ) -> dict[str, Any]:
        query: dict[str, Any] = {"path": path}
        if limit is not None:
            query["limit"] = limit
        if offset is not None:
            query["offset"] = offset
        resp = self._client.get(f"/threads/{thread_id}/files/history", query=query)
        return {
            "data": resp["data"],
            "hasMore": resp.get("has_more", False),
            "total": resp.get("total_count", 0),
        }

    def fork_from_message(self, thread_id: str, **params: Any) -> dict[str, Any]:
        aliases = {
            "truncate_at_message_index": "truncateAtMessageIndex",
            "environment_name": "environmentName",
            "environment_target": "environmentTarget",
            "environment_strategy": "environmentStrategy",
            "target_environment_id": "targetEnvironmentId",
            "file_copy_mode": "fileCopyMode",
        }
        body = {aliases.get(key, key): value for key, value in params.items() if value is not None}
        return self._client.post(f"/threads/{thread_id}/fork-from-message", body)

    def get_context_estimate(self, thread_id: str) -> dict[str, Any]:
        return self._client.get(f"/threads/{thread_id}/context")

    def get_context_details(self, thread_id: str) -> dict[str, Any]:
        return self._client.get(f"/threads/{thread_id}/context/details")

    def run_context_action(self, thread_id: str, *, action: str, prompt: str | None = None, title: str | None = None) -> dict[str, Any]:
        body: dict[str, Any] = {"action": action}
        if prompt is not None:
            body["prompt"] = prompt
        if title is not None:
            body["title"] = title
        return self._client.post(f"/threads/{thread_id}/context/actions", body)

    def generate_title(
        self,
        thread_id: str,
        *,
        message: str,
        content: str | None = None,
        task: str | None = None,
        force: bool | None = None,
    ) -> dict[str, Any]:
        body: dict[str, Any] = {"message": message}
        if content is not None:
            body["content"] = content
        if task is not None:
            body["task"] = task
        if force is not None:
            body["force"] = force
        return self._client.post(f"/threads/{thread_id}/generate-title", body)

    def get_diffs(
        self,
        thread_id: str,
        *,
        execution_id: str | None = None,
    ) -> list[dict[str, Any]]:
        resp = self._client.get(
            f"/threads/{thread_id}/diffs",
            query={"executionId": execution_id},
        )
        return resp.get("diffs") or resp.get("data") or []

    def get_feedback(self, thread_id: str) -> ThreadFeedbackSummary:
        """Get aggregated thumbs up/down feedback for a thread."""
        return self._client.get(f"/threads/{thread_id}/feedback")

    def set_feedback(self, thread_id: str, rating: str) -> ThreadFeedbackSummary:
        """Store the current user's thumbs up/down feedback for a thread."""
        return self._client.post(
            f"/threads/{thread_id}/feedback",
            {"rating": rating},
        )

    def report_issue(
        self,
        thread_id: str,
        *,
        report_type: str,
        message: str,
        metadata: dict[str, Any] | None = None,
    ) -> ThreadFeedbackReport:
        """Report qualitative feedback or an issue for a thread."""
        body: dict[str, Any] = {
            "reportType": report_type,
            "message": message,
        }
        if metadata is not None:
            body["metadata"] = metadata
        return self._client.post(f"/threads/{thread_id}/feedback/report", body)

    def report_feedback(
        self,
        thread_id: str,
        *,
        report_type: str,
        message: str,
        metadata: dict[str, Any] | None = None,
    ) -> ThreadFeedbackReport:
        """Alias for :meth:`report_issue`."""
        return self.report_issue(
            thread_id,
            report_type=report_type,
            message=message,
            metadata=metadata,
        )

    def list_permission_requests(self, thread_id: str) -> list[ThreadPermissionRequest]:
        """List pending runtime permission requests for a thread."""
        resp = self._client.get(f"/threads/{thread_id}/permission-requests")
        return resp["data"]

    def decide_permission_request(
        self,
        thread_id: str,
        request_id: str,
        *,
        decision: str,
        reason: str | None = None,
    ) -> ThreadPermissionDecisionResponse:
        """Approve or deny a runtime permission request."""
        body: dict[str, Any] = {"decision": decision}
        if reason is not None:
            body["reason"] = reason
        return self._client.post(
            f"/threads/{thread_id}/permission-requests/{request_id}/decision",
            body,
        )

    def approve_permission_request(
        self,
        thread_id: str,
        request_id: str,
        *,
        reason: str | None = None,
    ) -> ThreadPermissionDecisionResponse:
        """Approve a runtime permission request."""
        return self.decide_permission_request(
            thread_id,
            request_id,
            decision="allow",
            reason=reason,
        )

    def deny_permission_request(
        self,
        thread_id: str,
        request_id: str,
        *,
        reason: str | None = None,
    ) -> ThreadPermissionDecisionResponse:
        """Deny a runtime permission request."""
        return self.decide_permission_request(
            thread_id,
            request_id,
            decision="deny",
            reason=reason,
        )

    def list_research(self, thread_id: str) -> list[ResearchSession]:
        """List deep research sessions for a thread."""
        resp = self._client.get(f"/threads/{thread_id}/research")
        return resp["sessions"]

    def get_research(self, thread_id: str, session_id: str) -> ResearchSession:
        """Get a specific deep research session."""
        resp = self._client.get(f"/threads/{thread_id}/research/{session_id}")
        return resp["session"]

    def delete_research(self, thread_id: str, session_id: str) -> None:
        """Delete a deep research session."""
        self._client.delete(f"/threads/{thread_id}/research/{session_id}")

    def cancel(self, thread_id: str) -> None:
        """Cancel an in-progress message execution."""
        self._client.post(f"/threads/{thread_id}/cancel")
