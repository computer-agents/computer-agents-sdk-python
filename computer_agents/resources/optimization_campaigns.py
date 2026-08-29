"""Standalone, evidence-gated Optimization Campaigns."""

from __future__ import annotations

from typing import Any
from urllib.parse import quote

from .._api_client import ApiClient
from ..types import OptimizationCampaign, OptimizationCampaignContract


def _id(value: str) -> str:
    return quote(value, safe="")


class OptimizationCampaignsResource:
    """Operate Optimization Campaigns independently of Mission Control."""

    def __init__(self, client: ApiClient) -> None:
        self._client = client

    def list(
        self,
        *,
        project_id: str | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> dict[str, Any]:
        response = self._client.get(
            "/optimization-campaigns",
            query={
                "projectId": project_id,
                "limit": limit,
                "offset": offset,
            },
        )
        return {
            "data": response.get("data", response.get("campaigns", [])),
            "hasMore": response.get("hasMore", False),
        }

    def create(
        self,
        contract: OptimizationCampaignContract,
    ) -> dict[str, Any]:
        return self._client.post(
            "/optimization-campaigns",
            {"contract": contract},
        )

    def get(self, campaign_id: str) -> OptimizationCampaign:
        response = self._client.get(
            f"/optimization-campaigns/{_id(campaign_id)}",
        )
        return response["campaign"]

    def start(self, campaign_id: str) -> dict[str, Any]:
        return self._client.post(
            f"/optimization-campaigns/{_id(campaign_id)}/start",
            {},
        )

    def begin_production(
        self,
        campaign_id: str,
        attempt_id: str,
    ) -> dict[str, Any]:
        return self._client.post(
            (
                f"/optimization-campaigns/{_id(campaign_id)}"
                f"/attempts/{_id(attempt_id)}/begin"
            ),
            {},
        )

    def get_producer_context(
        self,
        campaign_id: str,
        attempt_id: str,
    ) -> dict[str, Any]:
        response = self._client.get(
            (
                f"/optimization-campaigns/{_id(campaign_id)}"
                f"/attempts/{_id(attempt_id)}/producer-context"
            ),
        )
        return response["context"]

    def report_production_failure(
        self,
        campaign_id: str,
        attempt_id: str,
        *,
        classification: str,
        error: str,
        retryable: bool,
        cost_usd: float | None = None,
    ) -> dict[str, Any]:
        body: dict[str, Any] = {
            "classification": classification,
            "error": error,
            "retryable": retryable,
        }
        if cost_usd is not None:
            body["costUsd"] = cost_usd
        return self._client.post(
            (
                f"/optimization-campaigns/{_id(campaign_id)}"
                f"/attempts/{_id(attempt_id)}/failure"
            ),
            body,
        )

    def submit_candidate(
        self,
        campaign_id: str,
        attempt_id: str,
        proposal: dict[str, Any],
        *,
        producer_cost_usd: float | None = None,
    ) -> dict[str, Any]:
        body: dict[str, Any] = {"proposal": proposal}
        if producer_cost_usd is not None:
            body["producerCostUsd"] = producer_cost_usd
        return self._client.post(
            (
                f"/optimization-campaigns/{_id(campaign_id)}"
                f"/attempts/{_id(attempt_id)}/candidate"
            ),
            body,
        )

    def reconcile_attempt(
        self,
        campaign_id: str,
        attempt_id: str,
    ) -> dict[str, Any]:
        return self._client.post(
            (
                f"/optimization-campaigns/{_id(campaign_id)}"
                f"/attempts/{_id(attempt_id)}/reconcile"
            ),
            {},
        )

    def finalize_attempt(
        self,
        campaign_id: str,
        attempt_id: str,
        assurance_run_id: str,
    ) -> dict[str, Any]:
        return self._client.post(
            (
                f"/optimization-campaigns/{_id(campaign_id)}"
                f"/attempts/{_id(attempt_id)}/finalize"
            ),
            {"assuranceRunId": assurance_run_id},
        )

    def promote_attempt(
        self,
        campaign_id: str,
        attempt_id: str,
        acceptance_fingerprint: str,
    ) -> dict[str, Any]:
        return self._client.post(
            (
                f"/optimization-campaigns/{_id(campaign_id)}"
                f"/attempts/{_id(attempt_id)}/promote"
            ),
            {"acceptanceFingerprint": acceptance_fingerprint},
        )

    def cancel(
        self,
        campaign_id: str,
        *,
        reason: str | None = None,
    ) -> OptimizationCampaign:
        response = self._client.post(
            f"/optimization-campaigns/{_id(campaign_id)}/cancel",
            {"reason": reason} if reason else {},
        )
        return response["campaign"]
