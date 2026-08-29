"""Materialized Function and Metronome optimization candidates."""

from __future__ import annotations

from typing import Any
from urllib.parse import quote

from .._api_client import ApiClient


def _id(value: str) -> str:
    return quote(value, safe="")


def _kind(value: str) -> str:
    if value not in {"function", "metronome"}:
        raise ValueError("target_kind must be 'function' or 'metronome'")
    return "functions" if value == "function" else "metronomes"


class OptimizationCandidatesResource:
    def __init__(self, client: ApiClient) -> None:
        self._client = client

    def list(
        self,
        target_kind: str,
        resource_id: str,
        *,
        limit: int | None = None,
        offset: int | None = None,
    ) -> dict[str, Any]:
        response = self._client.get(
            f"/optimization-candidates/{_kind(target_kind)}/{_id(resource_id)}",
            query={"limit": limit, "offset": offset},
        )
        return {
            "data": response.get("data", response.get("candidates", [])),
            "publishedBase": response.get("publishedBase"),
            "hasMore": response.get("hasMore", False),
        }

    def create(
        self,
        target_kind: str,
        resource_id: str,
        proposal: dict[str, Any],
    ) -> dict[str, Any]:
        return self._client.post(
            f"/optimization-candidates/{_kind(target_kind)}/{_id(resource_id)}",
            {"proposal": proposal},
        )

    def accept(
        self,
        target_kind: str,
        resource_id: str,
        candidate_id: str,
        *,
        evaluation_run_id: str,
        assurance_run_id: str,
    ) -> dict[str, Any]:
        return self._client.post(
            f"/optimization-candidates/{_kind(target_kind)}/{_id(resource_id)}"
            f"/{_id(candidate_id)}/accept",
            {
                "evaluationRunId": evaluation_run_id,
                "assuranceRunId": assurance_run_id,
            },
        )

    def promote(
        self,
        target_kind: str,
        resource_id: str,
        candidate_id: str,
        **params: Any,
    ) -> dict[str, Any]:
        return self._client.post(
            f"/optimization-candidates/{_kind(target_kind)}/{_id(resource_id)}"
            f"/{_id(candidate_id)}/promote",
            params,
        )
