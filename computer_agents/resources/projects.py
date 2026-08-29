"""Projects resource manager.

Handles organization-scoped planning projects and their delivery workflows.
"""

from __future__ import annotations

from typing import Any, List

from .._api_client import ApiClient
from ..types import (
    Project,
    CreateProjectWorkRelationParams,
    ProjectDeliveryContract,
    ProjectDeliveryDesign,
    ProjectDeliveryDesignRequest,
    ProjectDeliveryExecution,
    ProjectDeliveryPlan,
    ProjectDeliveryPreview,
    ProjectDetailResult,
    ProjectListResult,
    ProjectAgentSessionSummary,
    ProjectWorkGraph,
    ProjectWorkRelation,
    TaskAgentSessionListResult,
    ProjectOwnerCandidate,
    ProjectUpdateCommentResult,
    DeleteProjectUpdateCommentResult,
    ProjectUpdateListResult,
    ProjectUpdateReactionResult,
    ProjectUpdateResult,
    ProjectMentionCandidate,
    ProjectMissionControlRunResult,
    ProjectActivityCommentResult,
)


_FIELD_ALIASES = {
    "default_environment_id": "defaultEnvironmentId",
    "environment_ids": "environmentIds",
    "idempotency_key": "idempotencyKey",
    "parent_comment_id": "parentCommentId",
    "clone_project_directory": "cloneProjectDirectory",
    "permission_set": "permissionSet",
    "mission_control": "missionControl",
}


def _api_body(params: dict[str, Any]) -> dict[str, Any]:
    return {
        _FIELD_ALIASES.get(key, key): value
        for key, value in params.items()
        if value is not None
    }


class ProjectsResource:
    """Organization-scoped project management."""

    def __init__(self, client: ApiClient) -> None:
        self._client = client

    def list(
        self,
        *,
        type: str | None = None,
        q: str | None = None,
        limit: int | None = None,
        view: str | None = None,
    ) -> ProjectListResult:
        """List planning projects for the authenticated user.

        ``type`` and ``limit`` are retained as client-side compatibility
        filters; the current API accepts only ``q`` and ``view``.
        """
        query = {
            key: value
            for key, value in {"q": q, "view": view}.items()
            if value is not None
        }
        resp = self._client.get("/projects", query=query or None)
        matching = resp.get("data", [])
        if type is not None:
            matching = [project for project in matching if project.get("type") == type]
        data = matching[: max(0, limit)] if limit is not None else matching
        return {
            "data": data,
            "hasMore": bool(resp.get("has_more", False) or len(data) < len(matching)),
            "total": len(matching),
        }

    def create(self, name: str, **params: Any) -> Project:
        """Create a planning project."""
        current_fields = {
            "description",
            "color",
            "environment_ids",
            "environmentIds",
            "default_environment_id",
            "defaultEnvironmentId",
            "permission_set",
            "permissionSet",
            "metadata",
            "mission_control",
            "missionControl",
        }
        body = _api_body({
            key: value for key, value in params.items() if key in current_fields
        })
        resp = self._client.post("/projects", {"name": name, **body})
        return resp["project"]

    def get_by_id(
        self,
        project_id: str,
        *,
        view: str | None = None,
    ) -> ProjectDetailResult:
        """Get a planning project by ID."""
        query = {"view": view} if view is not None else None
        return self._client.get(f"/projects/{project_id}", query=query)

    def start_mission_control(
        self,
        project_id: str,
        *,
        agent_id: str,
        focus: dict[str, bool] | None = None,
        environment_id: str | None = None,
        instructions: str | None = None,
    ) -> ProjectMissionControlRunResult:
        """Start the platform-managed Mission Control workflow for a project."""
        body: dict[str, Any] = {"agentId": agent_id}
        if focus is not None:
            body["focus"] = focus
        if environment_id is not None:
            body["environmentId"] = environment_id
        if instructions is not None:
            body["instructions"] = instructions
        return self._client.post(
            f"/projects/{project_id}/mission-control/runs",
            body,
        )

    def list_mention_candidates(self, project_id: str) -> List[ProjectMentionCandidate]:
        """List organization members and accessible agents that may be mentioned."""
        response = self._client.get(f"/projects/{project_id}/mention-candidates")
        return response["data"]

    def create_activity_comment(
        self,
        project_id: str,
        event_id: str,
        *,
        body: str,
        idempotency_key: str | None = None,
        mentions: List[dict[str, str]] | None = None,
    ) -> ProjectActivityCommentResult:
        """Add a durable comment to one project activity event."""
        payload: dict[str, Any] = {"body": body}
        if idempotency_key is not None:
            payload["idempotencyKey"] = idempotency_key
        if mentions is not None:
            payload["mentions"] = mentions
        return self._client.post(
            f"/projects/{project_id}/activity/{event_id}/comments",
            payload,
        )

    def get_home(self, project_id: str) -> dict[str, Any]:
        return self._client.get(f"/projects/{project_id}/home")

    def start_automation(self, project_id: str, **params: Any) -> dict[str, Any]:
        body = _api_body(params)
        idempotency_key = str(body.get("idempotencyKey") or "").strip()
        return self._client.request(
            "POST",
            f"/projects/{project_id}/automation-runs",
            body=body,
            headers={"Idempotency-Key": idempotency_key} if idempotency_key else None,
        )

    def get_latest_automation(self, project_id: str) -> dict[str, Any]:
        return self._client.get(f"/projects/{project_id}/automation-runs/latest")

    def get_automation_run(self, project_id: str, run_id: str) -> dict[str, Any]:
        return self._client.get(f"/projects/{project_id}/automation-runs/{run_id}")

    def advance_automation_run(
        self,
        project_id: str,
        run_id: str,
        **params: Any,
    ) -> dict[str, Any]:
        return self._client.post(
            f"/projects/{project_id}/automation-runs/{run_id}/next",
            params,
        )

    def complete_automation_step(
        self,
        project_id: str,
        run_id: str,
        step_id: str,
        **params: Any,
    ) -> dict[str, Any]:
        return self._client.post(
            f"/projects/{project_id}/automation-runs/{run_id}/steps/{step_id}/complete",
            params,
        )

    def fail_automation_step(
        self,
        project_id: str,
        run_id: str,
        step_id: str,
        **params: Any,
    ) -> dict[str, Any]:
        return self._client.post(
            f"/projects/{project_id}/automation-runs/{run_id}/steps/{step_id}/fail",
            params,
        )

    def transition_automation_run(
        self,
        project_id: str,
        run_id: str,
        action: str,
    ) -> dict[str, Any]:
        if action not in {"pause", "resume", "cancel"}:
            raise ValueError("action must be pause, resume, or cancel")
        return self._client.post(
            f"/projects/{project_id}/automation-runs/{run_id}/{action}",
            {},
        )

    def update_by_id(self, project_id: str, **params: Any) -> Project:
        """Update a planning project by ID."""
        current_fields = {
            "name",
            "description",
            "color",
            "environment_ids",
            "environmentIds",
            "default_environment_id",
            "defaultEnvironmentId",
            "clone_project_directory",
            "cloneProjectDirectory",
            "permission_set",
            "permissionSet",
            "metadata",
            "mission_control",
            "missionControl",
        }
        resp = self._client.patch(
            f"/projects/{project_id}",
            _api_body({key: value for key, value in params.items() if key in current_fields}),
        )
        return resp["project"]

    def get_work_graph(self, project_id: str) -> ProjectWorkGraph:
        """Get tasks, normalized relations, and recent agent attempts."""
        return self._client.get(f"/projects/{project_id}/work-graph")

    def list_agent_sessions(
        self,
        project_id: str,
        *,
        limit: int | None = None,
    ) -> TaskAgentSessionListResult:
        """List durable task-agent execution attempts across a project."""
        resp = self._client.get(
            f"/projects/{project_id}/agent-sessions",
            query={"limit": limit} if limit is not None else None,
        )
        return {
            "data": resp.get("data", []),
            "hasMore": resp.get("has_more", False),
        }

    def get_agent_session_summary(
        self,
        project_id: str,
        *,
        window: str | None = None,
        stalled_after_minutes: int | None = None,
    ) -> ProjectAgentSessionSummary:
        """Summarize durable project task attempts, cost, and reliability."""
        query = {
            key: value
            for key, value in {
                "window": window,
                "stalledAfterMinutes": stalled_after_minutes,
            }.items()
            if value is not None
        }
        return self._client.get(
            f"/projects/{project_id}/agent-sessions/summary",
            query=query or None,
        )

    def create_work_relation(
        self,
        project_id: str,
        params: CreateProjectWorkRelationParams,
    ) -> ProjectWorkRelation:
        """Create a typed relation between two tasks in a project."""
        resp = self._client.post(
            f"/projects/{project_id}/work-relations",
            dict(params),
        )
        return resp["relation"]

    def delete_work_relation(
        self,
        project_id: str,
        relation_id: str,
    ) -> dict[str, bool]:
        """Delete a task relation from a project."""
        return self._client.delete(
            f"/projects/{project_id}/work-relations/{relation_id}",
        )

    def get_delivery_plan(self, project_id: str) -> ProjectDeliveryPlan:
        """Get the canonical Mission Control delivery plan and audit."""
        resp = self._client.get(f"/projects/{project_id}/delivery-plan")
        return resp["deliveryPlan"]

    def preview_delivery_design(
        self,
        project_id: str,
        request: ProjectDeliveryDesignRequest,
    ) -> dict[str, Any]:
        """Compile a project brief without persistence or other side effects."""
        return self._client.post(
            f"/projects/{project_id}/delivery-design/preview",
            {"request": request},
        )

    def get_delivery_design(self, project_id: str) -> ProjectDeliveryDesign:
        """Get the latest persisted delivery-design revision."""
        resp = self._client.get(f"/projects/{project_id}/delivery-design")
        return resp["deliveryDesign"]

    def put_delivery_design(
        self,
        project_id: str,
        request: ProjectDeliveryDesignRequest,
        *,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Persist a design revision without provisioning or execution."""
        body: dict[str, Any] = {"request": request}
        if idempotency_key:
            body["idempotencyKey"] = idempotency_key
        return self._client.request(
            "PUT",
            f"/projects/{project_id}/delivery-design",
            body=body,
            headers={"Idempotency-Key": idempotency_key} if idempotency_key else None,
        )

    def apply_delivery_design(
        self,
        project_id: str,
        *,
        design_fingerprint: str | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Apply the exact design as a plan without provisioning or starting."""
        body = {
            key: value
            for key, value in {
                "designFingerprint": design_fingerprint,
                "idempotencyKey": idempotency_key,
            }.items()
            if value is not None
        }
        return self._client.request(
            "POST",
            f"/projects/{project_id}/delivery-design/apply",
            body=body,
            headers={"Idempotency-Key": idempotency_key} if idempotency_key else None,
        )

    def preview_delivery_plan(
        self,
        project_id: str,
        contract: ProjectDeliveryContract,
    ) -> ProjectDeliveryPreview:
        """Strictly inspect a delivery contract without persisting resources."""
        resp = self._client.post(
            f"/projects/{project_id}/delivery-plan/preview",
            {"contract": contract},
        )
        return resp["preview"]

    def put_delivery_plan(
        self,
        project_id: str,
        contract: ProjectDeliveryContract,
        *,
        idempotency_key: str | None = None,
    ) -> ProjectDeliveryPlan:
        """Validate and persist a strict project-delivery contract."""
        payload: dict[str, Any] = {"contract": contract}
        if idempotency_key:
            payload["idempotencyKey"] = idempotency_key
        resp = self._client.request(
            "PUT",
            f"/projects/{project_id}/delivery-plan",
            body=payload,
            headers={"Idempotency-Key": idempotency_key} if idempotency_key else None,
        )
        return resp["deliveryPlan"]

    def archive_delivery_plan(self, project_id: str) -> ProjectDeliveryPlan:
        """Archive a terminal plan revision without deleting its audit."""
        resp = self._client.post(
            f"/projects/{project_id}/delivery-plan/archive",
            {},
        )
        return resp["deliveryPlan"]

    def provision_delivery_plan(self, project_id: str) -> ProjectDeliveryPlan:
        """Atomically create and bind the deterministic delivery graph."""
        resp = self._client.post(
            f"/projects/{project_id}/delivery-plan/provision",
            {},
        )
        return resp["deliveryPlan"]

    def get_delivery_execution(self, project_id: str) -> ProjectDeliveryExecution:
        """Get the latest durable, evidence-gated delivery execution."""
        resp = self._client.get(
            f"/projects/{project_id}/delivery-plan/execution",
        )
        return resp["deliveryExecution"]

    def start_delivery_execution(self, project_id: str) -> ProjectDeliveryExecution:
        """Idempotently start execution of the current ready plan revision."""
        resp = self._client.post(
            f"/projects/{project_id}/delivery-plan/execution/start",
            {},
        )
        return resp["deliveryExecution"]

    def reconcile_delivery_execution(self, project_id: str) -> ProjectDeliveryExecution:
        """Request an immediate idempotent server-side reconciliation."""
        resp = self._client.post(
            f"/projects/{project_id}/delivery-plan/execution/reconcile",
            {},
        )
        return resp["deliveryExecution"]

    def retry_delivery_execution(self, project_id: str) -> ProjectDeliveryExecution:
        """Retry the latest repairable delivery execution stage."""
        resp = self._client.post(
            f"/projects/{project_id}/delivery-plan/execution/retry",
            {},
        )
        return resp["deliveryExecution"]

    def cancel_delivery_execution(self, project_id: str) -> ProjectDeliveryExecution:
        """Cancel the latest non-terminal delivery execution."""
        resp = self._client.post(
            f"/projects/{project_id}/delivery-plan/execution/cancel",
            {},
        )
        return resp["deliveryExecution"]

    def list_owner_candidates(self, project_id: str) -> list[ProjectOwnerCandidate]:
        """List active organization members eligible to own a project."""
        resp = self._client.get(f"/projects/{project_id}/owner-candidates")
        return resp.get("data", [])

    def transfer_ownership(self, project_id: str, owner_user_id: str) -> Project:
        """Transfer canonical project ownership to an eligible organization member."""
        resp = self._client.patch(
            f"/projects/{project_id}/owner",
            {"ownerUserId": owner_user_id},
        )
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

    def list_updates(self, project_id: str) -> ProjectUpdateListResult:
        """List durable updates posted to a planning project."""
        resp = self._client.get(f"/projects/{project_id}/updates")
        data = resp.get("data", [])
        return {
            "data": data,
            "hasMore": resp.get("has_more", False),
            "total": resp.get("total_count", len(data)),
        }

    def create_update(
        self,
        project_id: str,
        body: str,
        **params: Any,
    ) -> ProjectUpdateResult:
        """Post a durable update and append it to project activity."""
        return self._client.post(
            f"/projects/{project_id}/updates",
            {"body": body, **_api_body(params)},
        )

    def create_update_comment(
        self,
        project_id: str,
        update_id: str,
        body: str,
        **params: Any,
    ) -> ProjectUpdateCommentResult:
        """Add a durable comment to a project update."""
        return self._client.post(
            f"/projects/{project_id}/updates/{update_id}/comments",
            {"body": body, **_api_body(params)},
        )

    def update_update_comment(
        self,
        project_id: str,
        update_id: str,
        comment_id: str,
        body: str,
    ) -> ProjectUpdateCommentResult:
        """Edit a project update comment authored by the current user."""
        return self._client.patch(
            f"/projects/{project_id}/updates/{update_id}/comments/{comment_id}",
            {"body": body},
        )

    def delete_update_comment(
        self,
        project_id: str,
        update_id: str,
        comment_id: str,
    ) -> DeleteProjectUpdateCommentResult:
        """Delete a project update comment authored by the current user."""
        return self._client.delete(
            f"/projects/{project_id}/updates/{update_id}/comments/{comment_id}",
        )

    def toggle_update_reaction(
        self,
        project_id: str,
        update_id: str,
        emoji: str,
    ) -> ProjectUpdateReactionResult:
        """Toggle the current user's emoji reaction on a project update."""
        return self._client.put(
            f"/projects/{project_id}/updates/{update_id}/reactions",
            {"emoji": emoji},
        )

    def get(self, project_id: str | None = None) -> Project:
        """Get a project, or resolve the only accessible project when omitted."""
        if project_id is not None:
            return self.get_by_id(project_id)["project"]
        projects = self.list(limit=2)["data"]
        if len(projects) == 1:
            return projects[0]
        if not projects:
            raise ValueError("No accessible project was found. Create a project or pass a project ID.")
        raise ValueError("More than one project is accessible. Pass a project ID explicitly.")

    def update(self, project_id: str | None = None, **params: Any) -> Project:
        """Update a project; pass an ID when more than one is accessible."""
        resolved_id = project_id or self.get()["id"]
        return self.update_by_id(resolved_id, **params)
