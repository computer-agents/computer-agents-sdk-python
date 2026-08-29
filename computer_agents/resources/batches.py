"""Durable, capacity-aware Batch queue and manual work shelf."""

from __future__ import annotations

from typing import Any
from urllib.parse import quote

from .._api_client import ApiClient


def _id(value: str) -> str:
    return quote(value, safe="")


class BatchesResource:
    def __init__(self, client: ApiClient) -> None:
        self._client = client

    def list(
        self,
        *,
        status: str | list[str] | None = None,
        project_id: str | None = None,
        ticket_id: str | None = None,
        limit: int | None = None,
        cursor: str | None = None,
    ) -> list[dict[str, Any]]:
        response = self._client.get(
            "/batch-jobs",
            query={
                "status": ",".join(status) if isinstance(status, list) else status,
                "projectId": project_id,
                "ticketId": ticket_id,
                "limit": limit,
                "cursor": cursor,
            },
        )
        return response.get("data", response.get("jobs", []))

    def get(self, batch_job_id: str) -> dict[str, Any]:
        return self._client.get(f"/batch-jobs/{_id(batch_job_id)}")

    def create(
        self,
        name: str,
        target_kind: str,
        *,
        idempotency_key: str | None = None,
        **params: Any,
    ) -> dict[str, Any]:
        body = {"name": name, "targetKind": target_kind, **params}
        if idempotency_key is not None:
            body["idempotencyKey"] = idempotency_key
        response = self._client.request(
            "POST",
            "/batch-jobs",
            body=body,
            headers={"Idempotency-Key": idempotency_key} if idempotency_key else None,
        )
        return response.get("job", response)

    def update(self, batch_job_id: str, **params: Any) -> dict[str, Any]:
        response = self._client.patch(f"/batch-jobs/{_id(batch_job_id)}", params)
        return response.get("job", response)

    def start(self, batch_job_id: str) -> dict[str, Any]:
        return self._transition(batch_job_id, "start")

    def hold(self, batch_job_id: str) -> dict[str, Any]:
        return self._transition(batch_job_id, "hold")

    def cancel(self, batch_job_id: str) -> dict[str, Any]:
        return self._transition(batch_job_id, "cancel")

    def reorder(self, batch_job_id: str, index: int) -> dict[str, Any]:
        response = self._client.post(
            f"/batch-jobs/{_id(batch_job_id)}/reorder",
            {"index": index},
        )
        return response.get("job", response)

    def delete(self, batch_job_id: str) -> bool:
        response = self._client.delete(f"/batch-jobs/{_id(batch_job_id)}")
        return response is None or response.get("deleted", True)

    def capacity(self) -> dict[str, Any]:
        return self._client.get("/batch-jobs/capacity")

    def process(self) -> dict[str, Any]:
        return self._client.post("/batch-jobs/process", {})

    def _transition(self, batch_job_id: str, action: str) -> dict[str, Any]:
        response = self._client.post(
            f"/batch-jobs/{_id(batch_job_id)}/{action}",
            {},
        )
        return response.get("job", response)
