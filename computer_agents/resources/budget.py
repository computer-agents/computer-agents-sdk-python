"""Budget & Billing resource managers.

Handles budget management, billing records, and usage tracking.
"""

from __future__ import annotations

from typing import Any

from .._api_client import ApiClient
from ..types import BudgetStatus


class BudgetResource:
    """Budget management.

    Example::

        status = client.budget.get_status()
        can_run = client.budget.can_execute()
    """

    def __init__(self, client: ApiClient) -> None:
        self._client = client

    def get_status(self) -> BudgetStatus:
        """Get the authenticated actor's current budget status."""
        resp = self._client.get("/billing/budget")
        spent_usd = resp.get(
            "currentPeriodUsageUsd",
            resp.get("currentPeriodUsage", resp.get("totalSpentUsd", resp.get("totalSpent", 0))),
        )
        limit_usd = resp.get("tierQuotaUsd", resp.get("tierQuota", resp.get("monthlyLimit", 0)))
        remaining_usd = resp.get("availableBudgetUsd", resp.get("availableBudget", max(0, limit_usd - spent_usd)))
        return {
            **resp,
            "balance": resp.get("balance", 0),
            "spent": spent_usd,
            "spentUsd": spent_usd,
            "currentPeriodUsageUsd": spent_usd,
            "limit": limit_usd,
            "limitUsd": limit_usd,
            "tierQuotaUsd": resp.get("tierQuotaUsd", resp.get("tierQuota", 0)),
            "remaining": remaining_usd,
            "remainingUsd": remaining_usd,
            "topUpBalanceUsd": resp.get("topUpBalanceUsd", resp.get("topUpBalance", 0)),
        }

    def get_cost_summary(
        self,
        *,
        project_id: str | None = None,
        period: str | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
    ) -> dict[str, Any]:
        """Get the current cost summary with optional API-supported filters."""
        return self._client.get(
            "/costs/summary",
            query={
                "projectId": project_id,
                "period": period,
                "startDate": start_date,
                "endDate": end_date,
            },
        )

    def get_breakdown(
        self,
        *,
        project_id: str | None = None,
        group_by: str | None = None,
        period: str | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
    ) -> dict[str, Any]:
        """Get detailed cost attribution by resource category."""
        return self._client.get(
            "/costs/breakdown",
            query={
                "projectId": project_id,
                "groupBy": group_by,
                "period": period,
                "startDate": start_date,
                "endDate": end_date,
            },
        )

    def get_thread_costs(
        self,
        *,
        project_id: str | None = None,
        limit: int | None = None,
        offset: int | None = None,
        sort_by: str | None = None,
        order: str | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
        agent_id: str | None = None,
        environment_id: str | None = None,
    ) -> dict[str, Any]:
        """Get per-thread cost attribution."""
        return self._client.get(
            "/costs/threads",
            query={
                "projectId": project_id,
                "limit": limit,
                "offset": offset,
                "sortBy": sort_by,
                "order": order,
                "startDate": start_date,
                "endDate": end_date,
                "agentId": agent_id,
                "environmentId": environment_id,
            },
        )

    def get_token_performance(
        self,
        *,
        period: str | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
    ) -> dict[str, Any]:
        """Get token and latency performance for model usage."""
        return self._client.get(
            "/costs/performance/tokens",
            query={"period": period, "startDate": start_date, "endDate": end_date},
        )

    def can_execute(self, estimated_cost: float | None = None) -> dict[str, Any]:
        """Check if execution is allowed given current budget.

        Budget checks are handled server-side during execution.
        """
        budget = self.get_status()
        estimated = estimated_cost or 0
        allowed = budget["remaining"] >= estimated
        if allowed:
            return {"canExecute": True}
        return {
            "canExecute": False,
            "reason": "Estimated cost exceeds the available budget",
        }

    def increase(
        self,
        amount_usd: float | None = None,
        *,
        amount: float | None = None,
        description: str | None = None,
    ) -> dict[str, Any]:
        """Increase budget using ``amount_usd`` or the legacy ``amount`` alias."""
        if amount_usd is None and amount is None:
            raise ValueError("amount_usd or amount is required")
        body: dict[str, Any] = {}
        if amount_usd is not None:
            body["amountUsd"] = amount_usd
        if amount is not None:
            body["amount"] = amount
        if description is not None:
            body["description"] = description
        return self._client.post("/billing/budget/increase", body)

    def get_records(
        self,
        *,
        limit: int | None = None,
        offset: int | None = None,
    ) -> dict[str, Any]:
        """Get billing records."""
        query: dict[str, Any] = {}
        if limit is not None:
            query["limit"] = limit
        if offset is not None:
            query["offset"] = offset
        resp = self._client.get("/billing/records", query=query or None)
        return {
            "records": resp["data"],
            "pagination": {
                "total": resp.get("total_count", 0),
                "limit": limit or 50,
                "offset": offset or 0,
            },
        }

class BillingResource:
    """Billing and usage tracking.

    Example::

        summary = client.billing.get_organization_summary()
        budget = client.billing.get_budget()
    """

    def __init__(self, client: ApiClient) -> None:
        self._client = client

    def get_catalog(self) -> dict[str, Any]:
        """Get the versioned public plan, entitlement, and usage-price catalog."""
        return self._client.get("/billing/catalog")

    def get_budget(self) -> dict[str, Any]:
        """Get the authenticated actor's current balance and usage controls."""
        return self._client.get("/billing/budget")

    def get_organization_summary(self, *, activity_limit: int | None = None) -> dict[str, Any]:
        """Get the active organization's ledger-backed billing summary."""
        query = {"activityLimit": activity_limit} if activity_limit is not None else None
        return self._client.get("/billing/organization/summary", query=query)

    def get_organization_plan(self) -> dict[str, Any]:
        """Get the effective plan and entitlements for the active organization."""
        return self._client.get("/billing/organization/plan")

    def get_organization_checkout_context(self) -> dict[str, Any]:
        """Verify that the active organization actor may start a checkout."""
        return self._client.get("/billing/organization/checkout-context")

    def update_organization_usage_controls(self, **params: Any) -> dict[str, Any]:
        """Update bounded metered-usage controls for the active organization."""
        return self._client.patch("/billing/organization/usage-controls", params)

    def get_preferences(self) -> dict[str, Any]:
        """Get billing and inference preferences for the active organization."""
        return self._client.get("/billing/preferences")

    def update_preferences(self, **params: Any) -> dict[str, Any]:
        """Update billing and inference preferences for the active organization."""
        return self._client.patch("/billing/preferences", params)

    def list_inference_endpoints(self) -> list[dict[str, Any]]:
        """List organization-managed inference endpoints."""
        resp = self._client.get("/billing/inference/endpoints")
        return resp.get("data") or resp.get("endpoints") or []

    def create_inference_endpoint(self, **params: Any) -> dict[str, Any]:
        """Create an organization-managed inference endpoint."""
        return self._client.post("/billing/inference/endpoints", params)

    def update_inference_endpoint(self, endpoint_id: str, **params: Any) -> dict[str, Any]:
        """Update an organization-managed inference endpoint."""
        return self._client.patch(f"/billing/inference/endpoints/{endpoint_id}", params)

    def delete_inference_endpoint(self, endpoint_id: str) -> dict[str, Any]:
        """Delete an organization-managed inference endpoint."""
        return self._client.delete(f"/billing/inference/endpoints/{endpoint_id}")

    def create_inference_endpoint_version(
        self,
        endpoint_id: str,
        **params: Any,
    ) -> dict[str, Any]:
        """Save an immutable inference endpoint configuration version."""
        return self._client.post(
            f"/billing/inference/endpoints/{endpoint_id}/versions",
            params,
        )

    def update_inference_endpoint_version(
        self,
        endpoint_id: str,
        version_id: str,
        **params: Any,
    ) -> dict[str, Any]:
        """Update a saved inference endpoint version."""
        return self._client.patch(
            f"/billing/inference/endpoints/{endpoint_id}/versions/{version_id}",
            params,
        )

    def publish_inference_endpoint_version(
        self,
        endpoint_id: str,
        version_id: str,
    ) -> dict[str, Any]:
        """Publish a saved inference endpoint version."""
        return self._client.post(
            f"/billing/inference/endpoints/{endpoint_id}/versions/{version_id}/publish",
            {},
        )

    def test_inference_endpoint(
        self,
        endpoint_id: str,
        **params: Any,
    ) -> dict[str, Any]:
        """Test an existing organization-managed inference endpoint."""
        return self._client.post(
            f"/billing/inference/endpoints/{endpoint_id}/test",
            params,
        )

    def test_inference_connection(self, **params: Any) -> dict[str, Any]:
        """Test a proposed or stored workspace inference connection."""
        return self._client.post("/billing/inference/test", params)
