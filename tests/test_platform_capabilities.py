from __future__ import annotations

from types import SimpleNamespace
from typing import Any

from computer_agents import ComputerAgentsClient
from computer_agents.resources.budget import BillingResource, BudgetResource
from computer_agents.resources.evidence import EvidenceResource
from computer_agents.resources.platform_administration import (
    AccountResource,
    AttachmentsResource,
)


MANAGER_ACCESSORS = (
    "account",
    "agents",
    "api_keys",
    "assurance",
    "attachments",
    "authorization",
    "batches",
    "billing",
    "budget",
    "computers",
    "databases",
    "email",
    "environments",
    "evaluations",
    "evidence",
    "files",
    "fine_tuning",
    "guardrails",
    "identity_connections",
    "knowledge",
    "local_bridge",
    "metronomes",
    "notifications",
    "optimization_campaigns",
    "optimization_candidates",
    "orchestrations",
    "organizations",
    "projects",
    "prompts",
    "release_control",
    "reports",
    "resources",
    "runtimes",
    "schedules",
    "security",
    "skills",
    "system",
    "tasks",
    "teams",
    "tests",
    "threads",
    "triggers",
    "voice_agents",
)


class RecordingClient:
    def __init__(self) -> None:
        self.calls: list[tuple[str, str, Any]] = []
        self.get_responses: list[dict[str, Any]] = []

    def get(self, path: str, query: dict[str, Any] | None = None) -> dict[str, Any]:
        self.calls.append(("GET", path, query))
        return self.get_responses.pop(0) if self.get_responses else {}

    def post(self, path: str, body: Any = None) -> dict[str, Any]:
        self.calls.append(("POST", path, body))
        return {"ok": True}

    def patch(self, path: str, body: Any = None) -> dict[str, Any]:
        self.calls.append(("PATCH", path, body))
        return {"ok": True}

    def delete(self, path: str, body: Any = None) -> dict[str, Any]:
        self.calls.append(("DELETE", path, body))
        return {"deleted": True}

    def request_raw(self, method: str, path: str) -> SimpleNamespace:
        self.calls.append((method, path, None))
        return SimpleNamespace(content=b"binary")


def test_client_initializes_every_tenant_facing_manager() -> None:
    with ComputerAgentsClient(api_key="tb_test") as client:
        for accessor in MANAGER_ACCESSORS:
            assert getattr(client, accessor) is not None, accessor
        assert callable(client.health)
        assert callable(client.ready)
        assert callable(client.metrics)


def test_evidence_review_routes_are_canonical_and_encoded() -> None:
    api = RecordingClient()
    api.get_responses = [
        {"open": 2},
        {"reviewTasks": [{"id": "review_1"}]},
        {"id": "review_1"},
    ]
    evidence = EvidenceResource(api)  # type: ignore[arg-type]

    evidence.get_overview("server/one")
    assert evidence.list_reviews("server/one", status="open") == [{"id": "review_1"}]
    evidence.get_review("server/one", "review/one")
    evidence.approve_review("server/one", "review/one", decisionNote="Verified")
    evidence.reject_review("server/one", "review/one", decisionNote="Unsupported")

    assert api.calls[0] == (
        "GET",
        "/servers/server%2Fone/evidence-agents/overview",
        None,
    )
    assert api.calls[1] == (
        "GET",
        "/servers/server%2Fone/evidence-agents/reviews",
        {"status": "open", "query": None, "limit": None, "offset": None},
    )
    assert api.calls[3] == (
        "POST",
        "/servers/server%2Fone/evidence-agents/reviews/review%2Fone/approve",
        {"decisionNote": "Verified"},
    )


def test_billing_and_inference_operations_use_versioned_routes() -> None:
    api = RecordingClient()
    api.get_responses = [
        {"catalogVersion": "v1"},
        {"endpoints": [{"id": "endpoint_1"}]},
    ]
    billing = BillingResource(api)  # type: ignore[arg-type]
    budget = BudgetResource(api)  # type: ignore[arg-type]

    billing.get_catalog()
    assert billing.list_inference_endpoints() == [{"id": "endpoint_1"}]
    billing.update_organization_usage_controls(overageEnabled=True)
    billing.create_inference_endpoint(name="DGX")
    billing.publish_inference_endpoint_version("endpoint_1", "version_1")
    budget.increase(10)

    assert (
        "PATCH",
        "/billing/organization/usage-controls",
        {"overageEnabled": True},
    ) in api.calls
    assert (
        "POST",
        "/billing/inference/endpoints/endpoint_1/versions/version_1/publish",
        {},
    ) in api.calls
    assert ("POST", "/billing/budget/increase", {"amountUsd": 10}) in api.calls


def test_account_and_attachment_binary_contracts() -> None:
    api = RecordingClient()
    account = AccountResource(api)  # type: ignore[arg-type]
    attachments = AttachmentsResource(api)  # type: ignore[arg-type]

    assert account.get_avatar("user/one") == b"binary"
    assert attachments.download("attachment/one") == b"binary"
    account.delete_data_category("threads")

    assert ("GET", "/account/avatar/user%2Fone", None) in api.calls
    assert ("GET", "/attachments/attachment%2Fone", None) in api.calls
    assert (
        "DELETE",
        "/account/data-controls/threads",
        {"confirmation": "threads"},
    ) in api.calls
