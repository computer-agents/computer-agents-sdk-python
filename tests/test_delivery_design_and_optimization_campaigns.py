from __future__ import annotations

from typing import Any

from computer_agents.resources.optimization_campaigns import (
    OptimizationCampaignsResource,
)
from computer_agents.resources.projects import ProjectsResource
from computer_agents.resources.release_control import ReleaseControlResource


class RecordingClient:
    def __init__(self) -> None:
        self.calls: list[tuple[Any, ...]] = []

    def get(
        self,
        path: str,
        *,
        query: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        self.calls.append(("GET", path, query))
        if path == "/optimization-campaigns":
            return {"data": [{"id": "campaign/one"}], "hasMore": False}
        if path.startswith("/optimization-campaigns/"):
            return {"campaign": {"id": "campaign/one"}}
        if path == "/release-control":
            return {
                "data": [{"id": "release/one"}],
                "hasMore": False,
                "limit": 20,
                "offset": 0,
            }
        if path == "/release-control/project-deliveries":
            return {
                "data": [{"id": "authorization/one"}],
                "hasMore": False,
                "limit": 20,
                "offset": 0,
            }
        if path.startswith("/release-control/project-deliveries/"):
            return {"authorization": {"id": "authorization/one"}}
        if path.startswith("/release-control/"):
            return {"release": {"id": "release/one"}}
        return {"deliveryDesign": {"id": "design-one"}}

    def post(self, path: str, body: dict[str, Any]) -> dict[str, Any]:
        self.calls.append(("POST", path, body))
        if path.endswith("/delivery-plan/archive"):
            return {"deliveryPlan": {"id": "plan-one", "status": "archived"}}
        if path == "/release-control/project-deliveries":
            return {
                "authorization": {"id": "authorization/one"},
                "created": True,
            }
        if path.startswith("/release-control/") and path.endswith("/cancel"):
            return {"release": {"id": "release/one", "status": "cancelled"}}
        if path.startswith("/release-control/"):
            return {"release": {"id": "release/one"}}
        if path == "/release-control":
            return {"release": {"id": "release/one"}, "created": True}
        if path.endswith("/cancel"):
            return {"campaign": {"id": "campaign/one", "status": "cancelled"}}
        return {"campaign": {"id": "campaign/one"}, "attempt": {"id": "attempt/one"}}

    def put(self, path: str, body: dict[str, Any]) -> dict[str, Any]:
        self.calls.append(("PUT", path, body))
        return {"deliveryDesign": {"id": "design-one"}, "alreadySaved": False}

    def request(
        self,
        method: str,
        path: str,
        *,
        body: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        self.calls.append((method, path, body, headers))
        return {"deliveryDesign": {"id": "design-one"}, "alreadySaved": False}


def test_project_delivery_design_has_separate_preview_save_and_apply() -> None:
    client = RecordingClient()
    projects = ProjectsResource(client)  # type: ignore[arg-type]
    request = {"brief": {"goal": "Build a verified workflow."}}

    projects.preview_delivery_design("project-one", request)  # type: ignore[arg-type]
    projects.get_delivery_design("project-one")
    projects.put_delivery_design(
        "project-one",
        request,  # type: ignore[arg-type]
        idempotency_key="delivery-design-one",
    )
    projects.apply_delivery_design(
        "project-one",
        design_fingerprint="sha256:" + ("a" * 64),
        idempotency_key="delivery-apply-one",
    )

    assert client.calls == [
        (
            "POST",
            "/projects/project-one/delivery-design/preview",
            {"request": request},
        ),
        ("GET", "/projects/project-one/delivery-design", None),
        (
            "PUT",
            "/projects/project-one/delivery-design",
            {"request": request, "idempotencyKey": "delivery-design-one"},
            {"Idempotency-Key": "delivery-design-one"},
        ),
        (
            "POST",
            "/projects/project-one/delivery-design/apply",
            {
                "designFingerprint": "sha256:" + ("a" * 64),
                "idempotencyKey": "delivery-apply-one",
            },
            {"Idempotency-Key": "delivery-apply-one"},
        ),
    ]


def test_project_delivery_plan_archive_has_an_explicit_sdk_command() -> None:
    client = RecordingClient()
    projects = ProjectsResource(client)  # type: ignore[arg-type]

    archived = projects.archive_delivery_plan("project-one")

    assert archived["status"] == "archived"
    assert client.calls == [
        (
            "POST",
            "/projects/project-one/delivery-plan/archive",
            {},
        ),
    ]


def test_optimization_campaign_resource_is_standalone_and_attempt_scoped() -> None:
    client = RecordingClient()
    campaigns = OptimizationCampaignsResource(client)  # type: ignore[arg-type]
    contract = {
        "name": "Improve extractor",
        "objective": {},
        "target": {},
        "producer": {},
        "evidence": {},
        "limits": {},
        "idempotencyKey": "campaign-one",
    }

    assert campaigns.list(project_id="project-one", limit=20)["hasMore"] is False
    assert campaigns.get("campaign/one")["id"] == "campaign/one"
    campaigns.create(contract)  # type: ignore[arg-type]
    campaigns.start("campaign/one")
    campaigns.promote_attempt(
        "campaign/one",
        "attempt/one",
        "sha256:" + ("b" * 64),
    )
    assert campaigns.cancel("campaign/one", reason="Operator stop")["status"] == "cancelled"

    assert (
        "POST",
        "/optimization-campaigns/campaign%2Fone/attempts/attempt%2Fone/promote",
        {"acceptanceFingerprint": "sha256:" + ("b" * 64)},
    ) in client.calls
    assert client.calls[-1] == (
        "POST",
        "/optimization-campaigns/campaign%2Fone/cancel",
        {"reason": "Operator stop"},
    )


def test_release_control_resource_never_accepts_caller_authored_evidence() -> None:
    client = RecordingClient()
    releases = ReleaseControlResource(client)  # type: ignore[arg-type]

    assert releases.list(project_id="project-one", limit=20)["hasMore"] is False
    assert releases.get("release/one")["id"] == "release/one"
    releases.create(
        target_kind="function",
        target_resource_id="function-one",
        candidate_id="candidate-one",
        acceptance_fingerprint="sha256:" + ("a" * 64),
        action="publish_and_deploy",
        project_id="project-one",
        idempotency_key="release-one",
    )
    releases.execute("release/one", expected_revision=1)
    releases.reconcile("release/one")
    assert releases.cancel("release/one", reason="Operator stop")["status"] == "cancelled"
    assert releases.list_project_delivery_authorizations(
        project_id="project-one",
        limit=20,
    )["hasMore"] is False
    assert releases.get_project_delivery_authorization(
        "authorization/one",
    )["id"] == "authorization/one"
    releases.authorize_project_delivery(
        delivery_execution_id="delivery-execution-one",
        idempotency_key="project-delivery-one",
    )

    assert (
        "POST",
        "/release-control",
        {
            "schemaVersion": "computer_agents_release_request_v1",
            "target": {
                "kind": "function",
                "resourceId": "function-one",
            },
            "candidate": {
                "id": "candidate-one",
                "acceptanceFingerprint": "sha256:" + ("a" * 64),
            },
            "action": "publish_and_deploy",
            "projectId": "project-one",
            "idempotencyKey": "release-one",
        },
    ) in client.calls
    assert (
        "POST",
        "/release-control/release%2Fone/reconcile",
        {},
    ) in client.calls
    assert (
        "POST",
        "/release-control/project-deliveries",
        {
            "schemaVersion":
                "computer_agents_project_delivery_release_request_v1",
            "deliveryExecutionId": "delivery-execution-one",
            "idempotencyKey": "project-delivery-one",
        },
    ) in client.calls
