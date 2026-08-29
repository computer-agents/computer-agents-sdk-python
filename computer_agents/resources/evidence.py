"""Scientific-evidence review and deterministic promotion operations."""

from __future__ import annotations

from typing import Any
from urllib.parse import quote

from .._api_client import ApiClient


class EvidenceResource:
    """Review extraction candidates and promote verified scientific evidence."""

    def __init__(self, client: ApiClient) -> None:
        self._client = client

    def get_overview(self, server_id: str) -> dict[str, Any]:
        """Get evidence-review and verified-evidence counts."""
        server = quote(server_id, safe="")
        return self._client.get(f"/servers/{server}/evidence-agents/overview")

    def list_reviews(
        self,
        server_id: str,
        *,
        status: str | None = None,
        query: str | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> list[dict[str, Any]]:
        """List extraction candidates in the evidence review queue."""
        server = quote(server_id, safe="")
        response = self._client.get(
            f"/servers/{server}/evidence-agents/reviews",
            query={
                "status": status,
                "query": query,
                "limit": limit,
                "offset": offset,
            },
        )
        return response.get("data") or response.get("reviews") or response.get("reviewTasks") or []

    def get_review(self, server_id: str, review_task_id: str) -> dict[str, Any]:
        """Get a review task with candidate, source evidence, and editable fields."""
        server = quote(server_id, safe="")
        task = quote(review_task_id, safe="")
        return self._client.get(f"/servers/{server}/evidence-agents/reviews/{task}")

    def approve_review(
        self,
        server_id: str,
        review_task_id: str,
        **params: Any,
    ) -> dict[str, Any]:
        """Validate and atomically promote reviewed evidence."""
        server = quote(server_id, safe="")
        task = quote(review_task_id, safe="")
        return self._client.post(
            f"/servers/{server}/evidence-agents/reviews/{task}/approve",
            params,
        )

    def reject_review(
        self,
        server_id: str,
        review_task_id: str,
        **params: Any,
    ) -> dict[str, Any]:
        """Reject an evidence candidate and append an audit event."""
        server = quote(server_id, safe="")
        task = quote(review_task_id, safe="")
        return self._client.post(
            f"/servers/{server}/evidence-agents/reviews/{task}/reject",
            params,
        )
