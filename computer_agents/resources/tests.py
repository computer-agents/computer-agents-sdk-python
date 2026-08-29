"""Tests resource manager."""

from __future__ import annotations

from typing import Any
from urllib.parse import quote

from .._api_client import ApiClient


def _id(value: str) -> str:
    return quote(value, safe="")


class TestsResource:
    """Deterministic test plans, immutable versions, runs, and evidence."""

    def __init__(self, client: ApiClient) -> None:
        self._client = client

    @staticmethod
    def _unwrap(response: Any, *keys: str) -> Any:
        if not isinstance(response, dict):
            return response
        for key in keys:
            value = response.get(key)
            if value is not None:
                return value
        return response

    def list(
        self,
        *,
        view: str | None = None,
        project_id: str | None = None,
        status: str | None = None,
        q: str | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> list[dict[str, Any]]:
        response = self._client.get(
            "/test-plans",
            query={
                "view": view,
                "projectId": project_id,
                "status": status,
                "q": q,
                "limit": limit,
                "offset": offset,
            },
        )
        return self._unwrap(response, "data", "testPlans") or []

    def get(self, test_plan_id: str) -> dict[str, Any]:
        response = self._client.get(f"/test-plans/{_id(test_plan_id)}")
        return self._unwrap(response, "testPlan", "data")

    def create(
        self,
        *,
        name: str,
        definition: dict[str, Any] | None = None,
        cases: list[dict[str, Any]] | None = None,
        publish_initial_version: bool | None = None,
        id: str | None = None,
        description: str | None = None,
        project_id: str | None = None,
        status: str | None = None,
        target_type: str | None = None,
        target_id: str | None = None,
        default_environment_id: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        body: dict[str, Any] = {"name": name}
        if definition is not None:
            body["definition"] = definition
        if cases is not None:
            body["cases"] = cases
        if publish_initial_version is not None:
            body["publishInitialVersion"] = publish_initial_version
        optional = {
            "id": id,
            "description": description,
            "projectId": project_id,
            "status": status,
            "targetType": target_type,
            "targetId": target_id,
            "defaultEnvironmentId": default_environment_id,
            "metadata": metadata,
        }
        body.update({key: value for key, value in optional.items() if value is not None})
        response = self._client.post("/test-plans", body)
        return self._unwrap(response, "testPlan", "data")

    def update(self, test_plan_id: str, **params: Any) -> dict[str, Any]:
        response = self._client.patch(f"/test-plans/{_id(test_plan_id)}", params)
        return self._unwrap(response, "testPlan", "data")

    def delete(self, test_plan_id: str) -> bool:
        response = self._client.delete(f"/test-plans/{_id(test_plan_id)}")
        if not isinstance(response, dict):
            return True
        return bool(response.get("deleted", response.get("success", True)))

    def list_versions(self, test_plan_id: str) -> list[dict[str, Any]]:
        response = self._client.get(f"/test-plans/{_id(test_plan_id)}/versions")
        return self._unwrap(response, "data", "versions") or []

    def create_version(
        self,
        test_plan_id: str,
        *,
        label: str | None = None,
        description: str | None = None,
        snapshot: dict[str, Any] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        body = {
            key: value
            for key, value in {
                "label": label,
                "description": description,
                "snapshot": snapshot,
                "metadata": metadata,
            }.items()
            if value is not None
        }
        response = self._client.post(
            f"/test-plans/{_id(test_plan_id)}/versions",
            body,
        )
        return self._unwrap(response, "version", "data")

    def publish_version(
        self,
        test_plan_id: str,
        version_id: str,
    ) -> dict[str, Any]:
        response = self._client.post(
            f"/test-plans/{_id(test_plan_id)}/versions/{_id(version_id)}/publish",
            {},
        )
        return self._unwrap(response, "testPlan", "data")

    def run(
        self,
        test_plan_id: str,
        *,
        version_id: str | None = None,
        environment_id: str | None = None,
        agent_id: str | None = None,
        project_id: str | None = None,
        task_id: str | None = None,
        release_id: str | None = None,
        trigger_type: str | None = None,
        commit_sha: str | None = None,
        run_id: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        body = {
            key: value
            for key, value in {
                "id": run_id,
                "versionId": version_id,
                "environmentId": environment_id,
                "agentId": agent_id,
                "projectId": project_id,
                "taskId": task_id,
                "releaseId": release_id,
                "triggerType": trigger_type,
                "commitSha": commit_sha,
                "metadata": metadata,
            }.items()
            if value is not None
        }
        response = self._client.post(
            f"/test-plans/{_id(test_plan_id)}/runs",
            body,
        )
        return self._unwrap(response, "testRun", "run", "data")

    def list_runs(
        self,
        *,
        test_plan_id: str | None = None,
        project_id: str | None = None,
        status: str | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> list[dict[str, Any]]:
        response = self._client.get(
            "/test-plans/runs",
            query={
                "testPlanId": test_plan_id,
                "projectId": project_id,
                "status": status,
                "limit": limit,
                "offset": offset,
            },
        )
        return self._unwrap(response, "data", "testRuns") or []

    def get_run(self, run_id: str) -> dict[str, Any]:
        response = self._client.get(f"/test-plans/runs/{_id(run_id)}")
        return self._unwrap(response, "testRun", "run", "data")

    def invoke_function_candidate(
        self,
        run_id: str,
        candidate_id: str,
        **params: Any,
    ) -> dict[str, Any]:
        return self._client.post(
            f"/test-plans/runs/{_id(run_id)}/function-candidates/{_id(candidate_id)}/invoke",
            params,
        )

    def acquire_run_lease(
        self,
        run_id: str,
        *,
        owner: str,
        ttl_ms: int | None = None,
    ) -> dict[str, Any]:
        response = self._client.post(
            f"/test-plans/runs/{_id(run_id)}/lease",
            {"owner": owner, "ttlMs": ttl_ms},
        )
        return self._unwrap(response, "lease")

    def heartbeat_run_lease(
        self,
        run_id: str,
        *,
        owner: str,
        token: str,
        ttl_ms: int | None = None,
    ) -> dict[str, Any]:
        response = self._client.post(
            f"/test-plans/runs/{_id(run_id)}/lease/heartbeat",
            {"owner": owner, "token": token, "ttlMs": ttl_ms},
        )
        return self._unwrap(response, "lease")

    def release_run_lease(
        self,
        run_id: str,
        *,
        owner: str,
        token: str,
    ) -> bool:
        response = self._client.request(
            "DELETE",
            f"/test-plans/runs/{_id(run_id)}/lease",
            body={"owner": owner, "token": token},
        )
        return bool(response.get("released")) if isinstance(response, dict) else False

    def report_run(self, run_id: str, **params: Any) -> dict[str, Any]:
        """Report progress or terminal results.

        Terminal runs and their server-issued evidence are immutable.
        """
        response = self._client.patch(f"/test-plans/runs/{_id(run_id)}", params)
        return self._unwrap(response, "testRun", "run", "data")
