"""Fine-tuning resource manager."""

from __future__ import annotations

from typing import Any
from urllib.parse import quote

from .._api_client import ApiClient


def _id(value: str) -> str:
    return quote(value, safe="")


class FineTuningResource:
    """Fine-tuning jobs that improve agents from evaluation sets."""

    def __init__(self, client: ApiClient) -> None:
        self._client = client

    @staticmethod
    def _unwrap(response: Any, *keys: str) -> Any:
        if not isinstance(response, dict):
            return response
        for key in ("data", *keys):
            value = response.get(key)
            if value is not None:
                return value
        return response

    def list_jobs(
        self,
        *,
        view: str | None = None,
        agent_id: str | None = None,
        evaluation_set_id: str | None = None,
        status: str | None = None,
        q: str | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> list[dict[str, Any]]:
        response = self._client.get(
            "/fine-tuning/jobs",
            query={
                "view": view,
                "agentId": agent_id,
                "evaluationSetId": evaluation_set_id,
                "status": status,
                "q": q,
                "limit": limit,
                "offset": offset,
            },
        )
        return self._unwrap(response, "jobs") or []

    def get_job(self, job_id: str) -> dict[str, Any]:
        response = self._client.get(f"/fine-tuning/jobs/{_id(job_id)}")
        return self._unwrap(response, "job")

    def create_job(
        self,
        *,
        agent_id: str,
        evaluation_set_ids: list[str],
        computer_id: str | None = None,
        environment_id: str | None = None,
        instructions: str | None = None,
        name: str | None = None,
        metadata: dict[str, Any] | None = None,
        queue_when_capacity_unavailable: bool | None = None,
    ) -> dict[str, Any]:
        """Start a fine-tuning job.

        Verification always runs after the generated agent version is created.
        There is intentionally no verification toggle.
        """
        body: dict[str, Any] = {
            "agentId": agent_id,
            "evaluationSetIds": evaluation_set_ids,
            "environmentId": environment_id or computer_id,
        }
        if instructions is not None:
            body["instructions"] = instructions
        if name is not None:
            body["name"] = name
        if metadata is not None:
            body["metadata"] = metadata
        if queue_when_capacity_unavailable is not None:
            body["queueWhenCapacityUnavailable"] = queue_when_capacity_unavailable
        response = self._client.post("/fine-tuning/jobs", body)
        if isinstance(response, dict) and response.get("queuedInBatch") is True:
            return response
        return self._unwrap(response, "job")

    def cancel_job(self, job_id: str) -> dict[str, Any]:
        response = self._client.post(f"/fine-tuning/jobs/{_id(job_id)}/cancel", {})
        return self._unwrap(response, "job")

    def update_job(self, job_id: str, **params: Any) -> dict[str, Any]:
        """Report worker progress or terminal optimization results."""
        response = self._client.patch(f"/fine-tuning/jobs/{_id(job_id)}", params)
        return self._unwrap(response, "job")

    def request_publication_approval(
        self,
        job_id: str,
        *,
        evidence_fingerprint: str,
    ) -> dict[str, Any]:
        return self._client.post(
            f"/fine-tuning/jobs/{_id(job_id)}/publication-approval",
            {"evidenceFingerprint": evidence_fingerprint},
        )

    def acquire_job_lease(
        self,
        job_id: str,
        *,
        owner: str,
        ttl_ms: int | None = None,
    ) -> dict[str, Any]:
        body: dict[str, Any] = {"owner": owner}
        if ttl_ms is not None:
            body["ttlMs"] = ttl_ms
        return self._client.post(f"/fine-tuning/jobs/{_id(job_id)}/lease", body)

    def heartbeat_job_lease(
        self,
        job_id: str,
        *,
        owner: str,
        token: str,
        ttl_ms: int | None = None,
    ) -> dict[str, Any]:
        body: dict[str, Any] = {"owner": owner, "token": token}
        if ttl_ms is not None:
            body["ttlMs"] = ttl_ms
        return self._client.post(
            f"/fine-tuning/jobs/{_id(job_id)}/lease/heartbeat",
            body,
        )

    def release_job_lease(self, job_id: str, *, owner: str, token: str) -> bool:
        response = self._client.delete(
            f"/fine-tuning/jobs/{_id(job_id)}/lease",
            {"owner": owner, "token": token},
        )
        return bool(response.get("released"))

    def queue_job(
        self,
        job_id: str,
        *,
        source: str | None = None,
        queue_when_capacity_unavailable: bool | None = None,
    ) -> dict[str, Any]:
        """Idempotently queue a planned optimization job."""
        body = {
            key: value
            for key, value in {
                "source": source,
                "queueWhenCapacityUnavailable": queue_when_capacity_unavailable,
            }.items()
            if value is not None
        }
        response = self._client.post(
            f"/fine-tuning/jobs/{_id(job_id)}/queue",
            body,
        )
        if isinstance(response, dict) and response.get("queuedInBatch") is True:
            return response
        return self._unwrap(response, "job")

    def delete_job(self, job_id: str) -> bool:
        response = self._client.delete(f"/fine-tuning/jobs/{_id(job_id)}")
        if not isinstance(response, dict):
            return True
        return bool(response.get("deleted", response.get("success", True)))
