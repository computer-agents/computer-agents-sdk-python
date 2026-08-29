"""Evaluations resource manager."""

from __future__ import annotations

from typing import Any, Literal
from urllib.parse import quote

from .._api_client import ApiClient
from .versioning import VersioningResource


def _id(value: str) -> str:
    return quote(value, safe="")


class EvaluationsResource:
    """Versioned evaluation datasets and runs."""

    def __init__(self, client: ApiClient) -> None:
        self._client = client
        self._versions = VersioningResource(client, "/evaluations")

    @staticmethod
    def _unwrap(response: Any, *keys: str) -> Any:
        if not isinstance(response, dict):
            return response
        for key in ("data", *keys):
            value = response.get(key)
            if value is not None:
                return value
        return response

    def list(
        self,
        *,
        view: Literal["summary"] | None = None,
        q: str | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> list[dict[str, Any]]:
        response = self._client.get(
            "/evaluations",
            query={"view": view, "q": q, "limit": limit, "offset": offset},
        )
        return self._unwrap(response, "evaluations", "sets") or []

    def get(
        self,
        evaluation_id: str,
        *,
        access_action: str | None = None,
    ) -> dict[str, Any]:
        response = self._client.get(
            f"/evaluations/{_id(evaluation_id)}",
            query={"accessAction": access_action},
        )
        return self._unwrap(response, "evaluation", "set")

    def create(
        self,
        *,
        name: str,
        description: str | None = None,
        cases: list[dict[str, Any]] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        body: dict[str, Any] = {"name": name}
        if description is not None:
            body["description"] = description
        if cases is not None:
            body["cases"] = cases
        if metadata is not None:
            body["metadata"] = metadata
        response = self._client.post("/evaluations", body)
        return self._unwrap(response, "evaluation", "set")

    def update(self, evaluation_id: str, **params: Any) -> dict[str, Any]:
        response = self._client.patch(f"/evaluations/{_id(evaluation_id)}", params)
        return self._unwrap(response, "evaluation", "set")

    def delete(self, evaluation_id: str) -> bool:
        response = self._client.delete(f"/evaluations/{_id(evaluation_id)}")
        if not isinstance(response, dict):
            return True
        return bool(response.get("deleted", response.get("success", True)))

    def import_dataset(self, **params: Any) -> dict[str, Any]:
        """Import a dataset and optional immutable source assets."""
        return self._client.post("/evaluations/imports", params)

    def get_observability(self, *, window_hours: int | None = None) -> dict[str, Any]:
        return self._client.get(
            "/evaluations/observability",
            query={"windowHours": window_hours},
        )

    def get_guardrail_overview(
        self,
        *,
        guardrail_id: str | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> dict[str, Any]:
        return self._client.get(
            "/evaluations/runs/guardrail-overview",
            query={"guardrailId": guardrail_id, "limit": limit, "offset": offset},
        )

    def run(
        self,
        evaluation_id: str,
        *,
        agent_id: str | None = None,
        run_id: str | None = None,
        target: dict[str, Any] | None = None,
        computer_id: str | None = None,
        environment_id: str | None = None,
        version_id: str | None = None,
        target_agent_version_id: str | None = None,
        purpose: Literal[
            "diagnostic",
            "development",
            "optimization",
            "release",
            "external_validation",
        ] = "diagnostic",
        label: str | None = None,
        metadata: dict[str, Any] | None = None,
        run: dict[str, Any] | None = None,
        queue_when_capacity_unavailable: bool | None = None,
    ) -> dict[str, Any]:
        """Run the latest published evaluation version unless version_id is supplied."""
        body: dict[str, Any] = {"purpose": purpose}
        if run_id is not None:
            body["id"] = run_id
        if target is not None:
            body["target"] = target
        if agent_id is not None:
            body["agentId"] = agent_id
        resolved_environment_id = environment_id or computer_id
        if resolved_environment_id is not None:
            body["environmentId"] = resolved_environment_id
        if version_id is not None:
            body["versionId"] = version_id
        if run is not None:
            body["run"] = run
        if target_agent_version_id is not None:
            body["run"] = {
                **(body.get("run") or {}),
                "targetAgentVersionId": target_agent_version_id,
            }
        if label is not None:
            body["label"] = label
        if metadata is not None:
            body["metadata"] = metadata
        if queue_when_capacity_unavailable is not None:
            body["queueWhenCapacityUnavailable"] = queue_when_capacity_unavailable
        response = self._client.post(f"/evaluations/{_id(evaluation_id)}/runs", body)
        if isinstance(response, dict) and response.get("queuedInBatch") is True:
            return response
        return self._unwrap(response, "run")

    def list_runs(
        self,
        *,
        evaluation_id: str | None = None,
        agent_id: str | None = None,
        status: str | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> list[dict[str, Any]]:
        response = self._client.get(
            "/evaluations/runs",
            query={
                "evaluationId": evaluation_id,
                "agentId": agent_id,
                "status": status,
                "limit": limit,
                "offset": offset,
            },
        )
        return self._unwrap(response, "runs") or []

    def get_run(self, run_id: str) -> dict[str, Any]:
        response = self._client.get(f"/evaluations/runs/{_id(run_id)}")
        return self._unwrap(response, "run")

    def report_run(
        self,
        run_id: str,
        *,
        status: str,
        results: list[dict[str, Any]] | None = None,
        metadata: dict[str, Any] | None = None,
        cost_usd: float | None = None,
        evaluator_fingerprint: str | None = None,
        system_fingerprint: str | None = None,
        execution_lease: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        """Report progress or terminal results; metrics and evidence are server-owned."""
        body: dict[str, Any] = {"status": status}
        if results is not None:
            body["results"] = results
        if metadata is not None:
            body["metadata"] = metadata
        if cost_usd is not None:
            body["costUsd"] = cost_usd
        if evaluator_fingerprint is not None:
            body["evaluatorFingerprint"] = evaluator_fingerprint
        if system_fingerprint is not None:
            body["systemFingerprint"] = system_fingerprint
        if execution_lease is not None:
            body["executionLease"] = execution_lease
        response = self._client.patch(f"/evaluations/runs/{_id(run_id)}", body)
        return self._unwrap(response, "run")

    def delete_run(self, run_id: str) -> bool:
        response = self._client.delete(f"/evaluations/runs/{_id(run_id)}")
        return response is None or response.get("deleted", True)

    def stage_source_asset(
        self,
        run_id: str,
        source_asset_id: str,
        *,
        case_id: str,
        execution_lease: dict[str, str],
    ) -> dict[str, Any]:
        return self._client.post(
            f"/evaluations/runs/{_id(run_id)}/source-assets/{_id(source_asset_id)}/stage",
            {"caseId": case_id, "executionLease": execution_lease},
        )

    def invoke_function_candidate(
        self,
        run_id: str,
        candidate_id: str,
        **params: Any,
    ) -> dict[str, Any]:
        return self._client.post(
            f"/evaluations/runs/{_id(run_id)}/function-candidates/{_id(candidate_id)}/invoke",
            params,
        )

    def acquire_run_lease(
        self,
        run_id: str,
        *,
        owner: str,
        ttl_ms: int | None = None,
    ) -> dict[str, Any]:
        body: dict[str, Any] = {"owner": owner}
        if ttl_ms is not None:
            body["ttlMs"] = ttl_ms
        return self._client.post(f"/evaluations/runs/{_id(run_id)}/lease", body)

    def heartbeat_run_lease(
        self,
        run_id: str,
        *,
        owner: str,
        token: str,
        ttl_ms: int | None = None,
    ) -> dict[str, Any]:
        body: dict[str, Any] = {"owner": owner, "token": token}
        if ttl_ms is not None:
            body["ttlMs"] = ttl_ms
        return self._client.post(
            f"/evaluations/runs/{_id(run_id)}/lease/heartbeat",
            body,
        )

    def release_run_lease(self, run_id: str, *, owner: str, token: str) -> bool:
        response = self._client.delete(
            f"/evaluations/runs/{_id(run_id)}/lease",
            {"owner": owner, "token": token},
        )
        return bool(response.get("released"))

    def list_dataset_assets(self, evaluation_id: str) -> list[dict[str, Any]]:
        response = self._client.get(
            f"/evaluations/{_id(evaluation_id)}/dataset-assets"
        )
        return response.get("data", response.get("datasetAssets", []))

    def download_dataset_asset(self, evaluation_id: str, asset_id: str) -> bytes:
        response = self._client.request_raw(
            "GET",
            f"/evaluations/{_id(evaluation_id)}/dataset-assets/{_id(asset_id)}/content",
        )
        return response.content

    def list_source_assets(
        self,
        evaluation_id: str,
        asset_id: str,
    ) -> list[dict[str, Any]]:
        response = self._client.get(
            f"/evaluations/{_id(evaluation_id)}/dataset-assets/{_id(asset_id)}/source-assets"
        )
        return response.get("data", response.get("sourceAssets", []))

    def download_source_asset(
        self,
        evaluation_id: str,
        asset_id: str,
        source_asset_id: str,
    ) -> bytes:
        response = self._client.request_raw(
            "GET",
            f"/evaluations/{_id(evaluation_id)}/dataset-assets/{_id(asset_id)}"
            f"/source-assets/{_id(source_asset_id)}/content",
        )
        return response.content

    def list_versions(self, evaluation_id: str) -> list[dict[str, Any]]:
        return self._versions.list(evaluation_id)

    def get_version(self, evaluation_id: str, version_id: str) -> dict[str, Any]:
        return self._versions.get(evaluation_id, version_id)

    def create_version(self, evaluation_id: str, **params: Any) -> dict[str, Any]:
        return self._versions.create(evaluation_id, **params)

    def update_version(self, evaluation_id: str, version_id: str, **params: Any) -> dict[str, Any]:
        return self._versions.update(evaluation_id, version_id, **params)

    def delete_version(self, evaluation_id: str, version_id: str) -> bool:
        return self._versions.delete(evaluation_id, version_id)

    def publish_version(
        self,
        evaluation_id: str,
        version_id: str,
        *,
        snapshot: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        params = {"snapshot": snapshot} if snapshot is not None else {}
        return self._versions.publish(evaluation_id, version_id, **params)

    def unpublish_version(self, evaluation_id: str, version_id: str) -> dict[str, Any]:
        return self._versions.unpublish(evaluation_id, version_id)

    def restore_version(self, evaluation_id: str, version_id: str) -> dict[str, Any]:
        return self._versions.restore(evaluation_id, version_id)

    def compare_versions(self, evaluation_id: str, *, base_version_id: str, target_version_id: str) -> dict[str, Any]:
        return self._versions.compare(
            evaluation_id,
            base_version_id=base_version_id,
            target_version_id=target_version_id,
        )
