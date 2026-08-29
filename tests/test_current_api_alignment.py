from __future__ import annotations

from typing import Any

from computer_agents.resources.agents import AgentsResource
from computer_agents.resources.budget import BudgetResource
from computer_agents.resources.environments import EnvironmentsResource
from computer_agents.resources.evaluations import EvaluationsResource
from computer_agents.resources.files import FilesResource
from computer_agents.resources.fine_tuning import FineTuningResource
from computer_agents.resources.git import GitResource
from computer_agents.resources.guardrails import GuardrailsResource
from computer_agents.resources.knowledge import KnowledgeResource
from computer_agents.resources.local_bridge import LocalBridgeResource
from computer_agents.resources.metronomes import MetronomesResource
from computer_agents.resources.orchestrations import OrchestrationsResource
from computer_agents.resources.organizations import OrganizationsResource
from computer_agents.resources.platform_administration import (
    ApiKeysResource,
    AuthorizationResource,
    EmailResource,
    ReportsResource,
    TeamsResource,
    VoiceAgentsResource,
)
from computer_agents.resources.product_resources import WebAppsResource
from computer_agents.resources.projects import ProjectsResource
from computer_agents.resources.resources import ResourcesResource
from computer_agents.resources.schedules import SchedulesResource
from computer_agents.resources.security import SecurityResource
from computer_agents.resources.tasks import TasksResource
from computer_agents.resources.tests import TestsResource as PlansResource
from computer_agents.resources.threads import ThreadsResource
from computer_agents.resources.triggers import TriggersResource


class RecordingClient:
    def __init__(self) -> None:
        self.calls: list[tuple[str, str, Any]] = []
        self.responses: dict[str, list[dict[str, Any]]] = {}

    def queue(self, method: str, *responses: dict[str, Any]) -> None:
        self.responses.setdefault(method, []).extend(responses)

    def _response(self, method: str) -> dict[str, Any]:
        queued = self.responses.get(method, [])
        return queued.pop(0) if queued else {}

    def get(self, path: str, query: dict[str, Any] | None = None) -> dict[str, Any]:
        self.calls.append(("GET", path, query))
        return self._response("GET")

    def post(self, path: str, body: Any = None) -> dict[str, Any]:
        self.calls.append(("POST", path, body))
        return self._response("POST")

    def patch(self, path: str, body: Any = None) -> dict[str, Any]:
        self.calls.append(("PATCH", path, body))
        return self._response("PATCH")

    def put(self, path: str, body: Any = None) -> dict[str, Any]:
        self.calls.append(("PUT", path, body))
        return self._response("PUT")

    def delete(self, path: str, body: Any = None) -> dict[str, Any]:
        self.calls.append(("DELETE", path, body))
        return self._response("DELETE")

    def request_form(
        self,
        method: str,
        path: str,
        *,
        data: dict[str, Any] | None = None,
        files: dict[str, Any] | None = None,
        timeout: float | None = None,
    ) -> dict[str, Any]:
        self.calls.append((method, path, {"data": data, "files": files, "timeout": timeout}))
        return self._response(method)

    def request(
        self,
        method: str,
        path: str,
        *,
        body: Any = None,
        query: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
        timeout: float | None = None,
    ) -> dict[str, Any]:
        self.calls.append((method, path, {"body": body, "query": query, "headers": headers, "timeout": timeout}))
        return self._response(method)

    def request_stream(
        self,
        method: str,
        path: str,
        *,
        body: Any = None,
        query: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
        timeout: float | None = None,
    ) -> Any:
        self.calls.append((method, path, {"body": body, "query": query, "headers": headers, "timeout": timeout}))
        return iter(self.responses.get(method, []))

    def request_raw(
        self,
        method: str,
        path: str,
        *,
        query: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
        timeout: float | None = None,
    ) -> Any:
        self.calls.append((method, path, {"query": query, "headers": headers, "timeout": timeout}))

        class RawResponse:
            content = b"thumbnail"

        return RawResponse()


def test_current_computer_envelopes_and_lifecycle_contracts() -> None:
    api = RecordingClient()
    api.queue("GET", {"environment": {"id": "env_1", "name": "Default"}})
    api.queue("PATCH", {"environment": {"id": "env_1"}})
    api.queue("PUT", {"environment": {"id": "env_1"}})
    api.queue(
        "POST",
        {"message": "Build started", "environmentId": "env_1", "buildStatus": "building"},
        {"status": "running", "containerId": "container_1", "message": "started"},
        {"status": "stopped", "message": "stopped"},
    )
    environments = EnvironmentsResource(api)  # type: ignore[arg-type]

    assert environments.get_default()["id"] == "env_1"
    environments.update("env_1", documentation=["README.md"])
    environments.replace("env_1", "Replacement", documentation=["RUNBOOK.md"])
    assert environments.trigger_build("env_1")["buildStatus"] == "building"
    assert environments.start(
        "env_1",
        agent_id="agent_1",
        enabled_skills={
            "customSkills": [{"id": "skill_1", "name": "Deploy", "markdown": "# Deploy"}],
        },
    )["status"] == "running"
    assert environments.stop("env_1")["status"] == "stopped"

    assert ("PATCH", "/environments/env_1", {"documentation": ["README.md"]}) in api.calls
    assert ("PUT", "/environments/env_1", {
        "name": "Replacement", "documentation": ["RUNBOOK.md"],
    }) in api.calls
    assert ("POST", "/environments/env_1/build", {}) in api.calls
    assert ("POST", "/environments/env_1/start", {
        "agentId": "agent_1",
        "enabledSkills": {
            "customSkills": [{"id": "skill_1", "name": "Deploy", "markdown": "# Deploy"}],
        },
    }) in api.calls
    assert ("POST", "/environments/env_1/stop", {}) in api.calls


def test_current_project_mission_control_mentions_and_activity_comments() -> None:
    api = RecordingClient()
    api.queue("GET", {"data": [{"kind": "human", "id": "user_1", "label": "Jan"}]})
    api.queue(
        "POST",
        {"thread": {"id": "thread_1"}, "run": {}, "metronome": {}, "output": None},
        {"comment": {"id": "comment_1"}, "project": {"id": "project_1"}},
    )
    projects = ProjectsResource(api)  # type: ignore[arg-type]

    projects.start_mission_control("project_1", agent_id="agent_1")
    assert len(projects.list_mention_candidates("project_1")) == 1
    projects.create_activity_comment(
        "project_1",
        "event_1",
        body="Please review this.",
        mentions=[{"kind": "agent", "id": "agent_1"}],
    )

    assert ("POST", "/projects/project_1/mission-control/runs", {"agentId": "agent_1"}) in api.calls
    assert ("GET", "/projects/project_1/mention-candidates", None) in api.calls
    assert ("POST", "/projects/project_1/activity/event_1/comments", {
        "body": "Please review this.",
        "mentions": [{"kind": "agent", "id": "agent_1"}],
    }) in api.calls


def test_current_github_automation_and_schedule_execution_contracts() -> None:
    api = RecordingClient()
    api.queue(
        "GET",
        {"data": [{"id": "binding_1"}]},
        {"data": [{"id": "execution_1"}]},
        {"data": [{"id": "schedule_execution_1"}], "has_more": True},
    )
    api.queue(
        "POST",
        {"binding": {"id": "binding_1"}},
        {"thread": {"id": "thread_1"}, "execution": {"id": "execution_1"}, "message": "started"},
    )
    api.queue("PATCH", {"binding": {"id": "binding_1"}})
    triggers = TriggersResource(api)  # type: ignore[arg-type]
    schedules = SchedulesResource(api)  # type: ignore[arg-type]

    triggers.list_github_automation_bindings(scope_type="project", scope_id="project_1")
    triggers.upsert_github_automation_binding(
        scope_type="project",
        scope_id="project_1",
        repository_full_name="computer-agents/sdk",
        kind="pull_request_review",
    )
    triggers.update_github_automation_binding("binding_1", enabled=False)
    triggers.delete_github_automation_binding("binding_1")
    triggers.list_github_automation_executions("binding_1", limit=10)
    assert schedules.list_executions(schedule_id="schedule_1", limit=25) == {
        "data": [{"id": "schedule_execution_1"}], "hasMore": True,
    }
    assert schedules.trigger("schedule_1")["message"] == "started"

    assert ("PATCH", "/github/automations/bindings/binding_1", {"enabled": False}) in api.calls
    assert ("DELETE", "/github/automations/bindings/binding_1", None) in api.calls
    assert ("GET", "/schedules/executions", {
        "scheduleId": "schedule_1", "limit": 25,
    }) in api.calls


def test_current_git_commit_and_push_contracts() -> None:
    api = RecordingClient()
    api.queue(
        "POST",
        {"success": True, "stagedFiles": ["src/app.py"], "message": "Staged 1 file(s)"},
        {"success": True, "sha": "abc1234", "message": "[main abc1234] Update"},
        {"success": True, "branch": "main", "message": "Push successful"},
    )
    git = GitResource(api)  # type: ignore[arg-type]

    assert git.commit(
        "env_1", "Update", path="repo", files=["src/app.py"],
    ) == {"success": True, "sha": "abc1234", "message": "[main abc1234] Update"}
    assert git.push(
        "env_1", path="repo", branch="main",
    ) == {"success": True, "branch": "main", "message": "Push successful"}

    assert api.calls[0] == (
        "POST", "/environments/env_1/git/stage",
        {"files": ["src/app.py"], "path": "repo"},
    )
    assert api.calls[1] == (
        "POST", "/environments/env_1/git/commit",
        {"message": "Update", "path": "repo"},
    )
    assert api.calls[2] == (
        "POST", "/environments/env_1/git/push",
        {"path": "repo", "branch": "main"},
    )


def test_current_thread_creation_filters_and_knowledge_contracts() -> None:
    api = RecordingClient()
    api.queue("POST", {
        "thread": {"id": "thread_1"},
        "queuedInBatch": True,
        "batchJobId": "batch_1",
        "admissionReason": "runtime_capacity_unavailable",
    })
    api.queue("GET", {"data": [], "has_more": False, "total_count": 0})
    threads = ThreadsResource(api)  # type: ignore[arg-type]

    thread = threads.create(
        project_id="project_1",
        content="Ship it",
        knowledge_context={"mode": "read", "source": "sdk", "libraryIds": ["knowledge_1"]},
        queue_when_capacity_unavailable=True,
    )
    assert thread["queuedInBatch"] is True
    assert thread["batchJobId"] == "batch_1"
    threads.list(
        project_id="project_1",
        agent_id="agent_1",
        app_id="runner",
        schedule_id="schedule_1",
        created_after="2026-08-01T00:00:00.000Z",
    )

    assert api.calls[0] == ("POST", "/threads", {
        "projectId": "project_1",
        "content": "Ship it",
        "queueWhenCapacityUnavailable": True,
        "knowledgeContext": {"mode": "read", "source": "sdk", "libraryIds": ["knowledge_1"]},
        "stream": False,
    })
    assert api.calls[1] == ("GET", "/threads", {
        "projectId": "project_1",
        "agentId": "agent_1",
        "appId": "runner",
        "scheduleId": "schedule_1",
        "createdAfter": "2026-08-01T00:00:00.000Z",
    })


def test_current_resource_budget_and_knowledge_parse_contracts() -> None:
    api = RecordingClient()
    api.queue(
        "POST",
        {"deployment": {"id": "deployment_1"}},
        {"success": True, "server": {"id": "server_1"}, "agentRuntime": {}, "decommissionedAt": "now"},
        {"success": True},
    )
    api.queue("GET", {
        "userId": "user_1",
        "planId": "pro",
        "balance": 12,
        "currentPeriodUsageUsd": 3,
        "tierQuotaUsd": 20,
        "availableBudgetUsd": 17,
        "usageBillingEnabled": True,
    })
    api.queue("POST", {
        "object": "knowledge.document_parse",
        "markdown": "# Brief",
        "provider": "firecrawl",
        "metadata": {},
        "conversion": {},
    })
    resources = ResourcesResource(api)  # type: ignore[arg-type]
    budget = BudgetResource(api)  # type: ignore[arg-type]
    knowledge = KnowledgeResource(api)  # type: ignore[arg-type]

    resources.deploy("server_1", version_id="version_2")
    resources.decommission("server_1")
    status = budget.get_status()
    assert status["userId"] == "user_1"
    assert status["planId"] == "pro"
    assert status["spent"] == 3
    assert status["limit"] == 20
    assert status["remaining"] == 17
    budget.increase(25, description="Release testing")
    parsed = knowledge.parse_document(
        "brief.docx",
        b"document bytes",
        content_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    )
    assert parsed["markdown"] == "# Brief"

    assert ("POST", "/servers/server_1/deploy", {"versionId": "version_2"}) in api.calls
    assert ("POST", "/servers/server_1/decommission", {}) in api.calls
    assert ("POST", "/billing/budget/increase", {
        "amountUsd": 25, "description": "Release testing",
    }) in api.calls
    parse_call = api.calls[-1]
    assert parse_call[0:2] == ("POST", "/knowledge/parse")
    assert parse_call[2]["files"]["file"] == (
        "brief.docx",
        b"document bytes",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    )


def test_capacity_receipts_and_execution_leases_are_preserved() -> None:
    api = RecordingClient()
    evaluation_receipt = {
        "run": None,
        "queuedInBatch": True,
        "batchJobId": "batch_eval",
        "batchJob": {"id": "batch_eval"},
    }
    fine_tuning_receipt = {
        "job": None,
        "queuedInBatch": True,
        "batchJobId": "batch_fine",
        "batchJob": {"id": "batch_fine"},
    }
    api.queue(
        "POST",
        evaluation_receipt,
        {"lease": {"runId": "run_1"}, "run": {"id": "run_1"}},
        {"lease": {"runId": "run_1"}},
        fine_tuning_receipt,
        {"lease": {"jobId": "job_1"}, "job": {"id": "job_1"}},
        {"lease": {"jobId": "job_1"}},
    )
    api.queue("DELETE", {"released": True}, {"released": True})
    evaluations = EvaluationsResource(api)  # type: ignore[arg-type]
    fine_tuning = FineTuningResource(api)  # type: ignore[arg-type]

    assert evaluations.run(
        "evaluation/1",
        agent_id="agent_1",
        queue_when_capacity_unavailable=True,
    ) == evaluation_receipt
    evaluations.acquire_run_lease("run/1", owner="worker_1", ttl_ms=90_000)
    evaluations.heartbeat_run_lease(
        "run/1", owner="worker_1", token="lease_1", ttl_ms=120_000,
    )
    assert evaluations.release_run_lease(
        "run/1", owner="worker_1", token="lease_1",
    ) is True

    assert fine_tuning.create_job(
        agent_id="agent_1",
        evaluation_set_ids=["evaluation_1"],
        environment_id="environment_1",
        queue_when_capacity_unavailable=True,
    ) == fine_tuning_receipt
    fine_tuning.acquire_job_lease("job/1", owner="worker_1", ttl_ms=90_000)
    fine_tuning.heartbeat_job_lease(
        "job/1", owner="worker_1", token="lease_1", ttl_ms=120_000,
    )
    assert fine_tuning.release_job_lease(
        "job/1", owner="worker_1", token="lease_1",
    ) is True

    assert ("POST", "/evaluations/evaluation%2F1/runs", {
        "agentId": "agent_1",
        "purpose": "diagnostic",
        "queueWhenCapacityUnavailable": True,
    }) in api.calls
    assert ("POST", "/evaluations/runs/run%2F1/lease", {
        "owner": "worker_1", "ttlMs": 90_000,
    }) in api.calls
    assert ("POST", "/evaluations/runs/run%2F1/lease/heartbeat", {
        "owner": "worker_1", "token": "lease_1", "ttlMs": 120_000,
    }) in api.calls
    assert ("DELETE", "/evaluations/runs/run%2F1/lease", {
        "owner": "worker_1", "token": "lease_1",
    }) in api.calls
    assert ("POST", "/fine-tuning/jobs/job%2F1/lease", {
        "owner": "worker_1", "ttlMs": 90_000,
    }) in api.calls
    assert ("POST", "/fine-tuning/jobs/job%2F1/lease/heartbeat", {
        "owner": "worker_1", "token": "lease_1", "ttlMs": 120_000,
    }) in api.calls
    assert ("DELETE", "/fine-tuning/jobs/job%2F1/lease", {
        "owner": "worker_1", "token": "lease_1",
    }) in api.calls


def test_metronome_batch_receipt_and_legacy_offset_are_handled_client_side() -> None:
    api = RecordingClient()
    api.queue("POST", {
        "data": {"id": "run_1", "status": "paused"},
        "queuedInBatch": True,
        "batchJob": {"id": "batch_1"},
    })
    api.queue("GET", {
        "data": [{"id": f"run_{index}"} for index in range(5)],
    })
    metronomes = MetronomesResource(api)  # type: ignore[arg-type]

    run = metronomes.run(
        "metronome_1",
        queue_when_capacity_unavailable=True,
    )
    assert run["queuedInBatch"] is True
    assert run["batchJobId"] == "batch_1"
    assert run["batchJob"] == {"id": "batch_1"}
    assert metronomes.list_runs("metronome_1", offset=2, limit=2) == [
        {"id": "run_2"}, {"id": "run_3"},
    ]
    assert ("GET", "/metronomes/metronome_1/runs", {"limit": 4}) in api.calls


def test_email_pagination_and_current_message_queries_are_preserved() -> None:
    api = RecordingClient()
    api.queue(
        "GET",
        {
            "messages": [{"id": "message_1"}],
            "nextPageToken": "page_2",
            "resultSizeEstimate": 12,
        },
        {"id": "message_1", "body": "Hello"},
    )
    email = EmailResource(api)  # type: ignore[arg-type]

    page = email.list_messages_page(
        max_results=25,
        q="from:release@example.com",
        cursor="legacy_page",
        include_body=True,
        label_ids=["INBOX", "STARRED"],
    )
    assert page["nextPageToken"] == "page_2"
    email.get_message("message/one", include_body=True)

    assert api.calls[0] == ("GET", "/email/messages", {
        "limit": 25,
        "q": "from:release@example.com",
        "pageToken": "legacy_page",
        "includeBody": True,
        "labelIds": ["INBOX", "STARRED"],
    })
    assert api.calls[1] == (
        "GET", "/email/messages/message%2Fone", {"includeBody": True},
    )


def test_every_current_specialized_query_control_is_forwarded() -> None:
    api = RecordingClient()
    api.queue("GET", *({"data": []} for _ in range(13)))
    resources = ResourcesResource(api)  # type: ignore[arg-type]
    files = FilesResource(api)  # type: ignore[arg-type]
    api_keys = ApiKeysResource(api)  # type: ignore[arg-type]
    voice_agents = VoiceAgentsResource(api)  # type: ignore[arg-type]
    orchestrations = OrchestrationsResource(api)  # type: ignore[arg-type]
    reports = ReportsResource(api)  # type: ignore[arg-type]
    authorization = AuthorizationResource(api)  # type: ignore[arg-type]
    guardrails = GuardrailsResource(api)  # type: ignore[arg-type]
    evaluations = EvaluationsResource(api)  # type: ignore[arg-type]
    metronomes = MetronomesResource(api)  # type: ignore[arg-type]
    security = SecurityResource(api)  # type: ignore[arg-type]

    resources.get_custom_domain("server/one", domain="app.example.com")
    resources.delete_custom_domain("server/one", domain="app.example.com")
    assert files.download_thumbnail(
        "environment/one", "images/logo.png", width=320, height=180,
    ) == b"thumbnail"
    api_keys.analytics(period="week")
    voice_agents.list_sessions(
        agent_id="agent_1",
        thread_id="thread_1",
        channel="phone",
        limit=20,
        offset=40,
    )
    orchestrations.list(
        environment_id="environment_1", status="active", limit=10, offset=5,
    )
    reports.list(limit=25, offset=50)
    authorization.policy_versions(
        resource_type="project", resource_id="project_1", limit=15,
    )
    authorization.list_delegations(
        principal_id="agent_1", status="active", limit=20,
    )
    authorization.list_approvals(
        principal_id="agent_1", status="pending", limit=20,
    )
    authorization.list_decisions(
        resource_type="project",
        resource_id="project_1",
        principal_id="agent_1",
        limit=20,
    )
    guardrails.get_evaluation_target("guardrail_1", version_id="version_2")
    evaluations.get("evaluation/one", access_action="evaluation_run")
    evaluations.get_guardrail_overview(
        guardrail_id="guardrail_1", limit=10, offset=20,
    )
    metronomes.get_run_timeline("metronome_1", "run_1", view="compact")
    security.queue_run(
        "repository/one", ref="main", idempotency_key="scan_retry_1",
    )
    security.create_remediation(
        "run/one", ["finding_1"], idempotency_key="remediation_retry_1",
    )

    assert ("GET", "/servers/server%2Fone/custom-domain", {
        "domain": "app.example.com",
    }) in api.calls
    assert ("DELETE", "/servers/server%2Fone/custom-domain", {
        "body": None,
        "query": {"domain": "app.example.com"},
        "headers": None,
        "timeout": None,
    }) in api.calls
    assert ("GET", "/environments/environment%2Fone/files/thumbnail/images/logo.png", {
        "query": {"w": 320, "h": 180}, "headers": None, "timeout": None,
    }) in api.calls
    assert ("GET", "/api-keys/analytics/overview", {"period": "week"}) in api.calls
    assert ("GET", "/voice-agents/sessions", {
        "agentId": "agent_1", "threadId": "thread_1", "channel": "phone",
        "limit": 20, "offset": 40,
    }) in api.calls
    assert ("GET", "/orchestrations", {
        "environmentId": "environment_1", "status": "active", "limit": 10, "offset": 5,
    }) in api.calls
    assert ("GET", "/reports", {"limit": 25, "offset": 50}) in api.calls
    assert ("GET", "/authorization/policy-versions", {
        "resourceType": "project", "resourceId": "project_1", "limit": 15,
    }) in api.calls
    assert ("GET", "/authorization/delegations", {
        "principalId": "agent_1", "status": "active", "limit": 20,
    }) in api.calls
    assert ("GET", "/authorization/approvals", {
        "principalId": "agent_1", "status": "pending", "limit": 20,
    }) in api.calls
    assert ("GET", "/authorization/decisions", {
        "resourceType": "project", "resourceId": "project_1",
        "principalId": "agent_1", "limit": 20,
    }) in api.calls
    assert ("GET", "/guardrails/guardrail_1/evaluation-target", {
        "versionId": "version_2",
    }) in api.calls
    assert ("GET", "/evaluations/evaluation%2Fone", {
        "accessAction": "evaluation_run",
    }) in api.calls
    assert ("GET", "/evaluations/runs/guardrail-overview", {
        "guardrailId": "guardrail_1", "limit": 10, "offset": 20,
    }) in api.calls
    assert ("GET", "/metronomes/metronome_1/runs/run_1/timeline", {
        "view": "compact",
    }) in api.calls
    assert ("POST", "/security/repositories/repository%2Fone/runs", {
        "body": {"ref": "main"},
        "query": None,
        "headers": {"Idempotency-Key": "scan_retry_1"},
        "timeout": None,
    }) in api.calls
    assert ("POST", "/security/runs/run%2Fone/remediations", {
        "body": {"findingIds": ["finding_1"]},
        "query": None,
        "headers": {"Idempotency-Key": "remediation_retry_1"},
        "timeout": None,
    }) in api.calls


def test_snake_case_query_filters_use_canonical_wire_names() -> None:
    api = RecordingClient()
    api.queue("GET", *({"data": []} for _ in range(5)))
    local_bridge = LocalBridgeResource(api)  # type: ignore[arg-type]
    security = SecurityResource(api)  # type: ignore[arg-type]
    resources = ResourcesResource(api)  # type: ignore[arg-type]
    tasks = TasksResource(api)  # type: ignore[arg-type]
    threads = ThreadsResource(api)  # type: ignore[arg-type]

    local_bridge.list_bindings(
        device_id="device_1",
        environment_id="environment_1",
        project_id="project_1",
        limit=20,
        offset=40,
    )
    security.list_findings(
        repository_id="repository_1",
        run_id="run_1",
        status="open",
        severity="high",
        limit=25,
    )
    resources.list_runtime_database_documents(
        "server_1",
        "collection_1",
        limit=50,
        page_token="page_2",
    )
    tasks.list_global_activity(project_id="project_1", limit=10)
    threads.get_actions(
        "thread_1",
        run_id="run_1",
        group_id="group_1",
        after="event_1",
        limit=15,
        include_legacy=True,
    )

    assert api.calls == [
        ("GET", "/workspace-bindings", {
            "deviceId": "device_1",
            "environmentId": "environment_1",
            "projectId": "project_1",
            "limit": 20,
            "offset": 40,
        }),
        ("GET", "/security/findings", {
            "repositoryId": "repository_1",
            "runId": "run_1",
            "status": "open",
            "severity": "high",
            "limit": 25,
        }),
        ("GET", "/servers/server_1/runtime/database/collections/collection_1/documents", {
            "limit": 50,
            "pageToken": "page_2",
        }),
        ("GET", "/tasks/activity", {"projectId": "project_1", "limit": 10}),
        ("GET", "/threads/thread_1/actions", {
            "runId": "run_1",
            "groupId": "group_1",
            "after": "event_1",
            "limit": 15,
            "includeLegacy": True,
        }),
    ]


def test_current_thread_history_log_step_and_diff_queries_are_forwarded() -> None:
    api = RecordingClient()
    api.queue(
        "GET",
        {"data": [], "has_more": False, "total_count": 0},
        {"logs": []},
        {"data": []},
        {"diffs": []},
    )
    threads = ThreadsResource(api)  # type: ignore[arg-type]

    threads.get_messages("thread_1", limit=10, offset=20, order="desc", compact=True)
    threads.get_logs("thread_1", compact=True, include_conversation=False)
    threads.list_steps("thread_1", limit=5, offset=10, compact=True)
    threads.get_diffs("thread_1", execution_id="execution_1")

    assert api.calls[0] == ("GET", "/threads/thread_1/messages", {
        "limit": 10, "offset": 20, "order": "desc", "compact": True,
    })
    assert api.calls[1] == ("GET", "/threads/thread_1/logs", {
        "compact": True, "includeConversation": False,
    })
    assert api.calls[2] == ("GET", "/threads/thread_1/steps", {
        "limit": 5, "offset": 10, "compact": True,
    })
    assert api.calls[3] == ("GET", "/threads/thread_1/diffs", {
        "executionId": "execution_1",
    })


def test_project_runtime_whitelist_and_metadata_view() -> None:
    api = RecordingClient()
    api.queue("POST", {"project": {"id": "project_1"}})
    api.queue("PATCH", {"project": {"id": "project_1"}})
    api.queue("GET", {"project": {"id": "project_1"}})
    projects = ProjectsResource(api)  # type: ignore[arg-type]

    projects.create(
        "Release",
        id="ignored",
        description="SDK release",
        type="cloud",
        sources=[{"type": "github", "url": "https://example.test/repo"}],
        tags=["sdk"],
        color="#fff",
        environment_ids=["environment_1"],
    )
    projects.update_by_id(
        "project_1",
        name="Release ready",
        tags=["ignored"],
        clone_project_directory=True,
    )
    projects.get_by_id("project_1", view="metadata")

    assert api.calls[0] == ("POST", "/projects", {
        "name": "Release",
        "description": "SDK release",
        "color": "#fff",
        "environmentIds": ["environment_1"],
    })
    assert api.calls[1] == ("PATCH", "/projects/project_1", {
        "name": "Release ready",
        "cloneProjectDirectory": True,
    })
    assert api.calls[2] == ("GET", "/projects/project_1", {"view": "metadata"})


def test_resource_kind_and_period_queries_reach_product_facades() -> None:
    api = RecordingClient()
    api.queue(
        "GET",
        {"data": [{"id": "server_1", "kind": "web_app"}]},
        {"requests": []},
        {"data": [{"id": "server_1", "kind": "web_app"}]},
        {"requests": []},
        {"totals": {}},
    )
    resources = ResourcesResource(api)  # type: ignore[arg-type]
    web_apps = WebAppsResource(api)  # type: ignore[arg-type]

    resources.list(kind="web_app", project_id="project_1", limit=5)
    resources.get_analytics("server_1", period="week")
    web_apps.list(project_id="project_1", limit=5)
    web_apps.get_analytics("server_1", period="month")
    resources.get_overview_analytics(kind="web_app", period="day")

    assert api.calls[0] == ("GET", "/servers", {
        "kind": "web_app", "projectId": "project_1", "limit": 5,
    })
    assert api.calls[1] == ("GET", "/servers/server_1/analytics", {"period": "week"})
    assert api.calls[2] == ("GET", "/servers", {
        "kind": "web_app", "projectId": "project_1", "limit": 5,
    })
    assert api.calls[3] == ("GET", "/servers/server_1/analytics", {"period": "month"})
    assert api.calls[4] == ("GET", "/servers/analytics/overview", {
        "kind": "web_app", "period": "day",
    })


def test_guardrail_bindings_use_only_the_canonical_field() -> None:
    api = RecordingClient()
    api.queue(
        "PUT",
        {"agent": {"id": "agent_1"}},
        {"agent": {"id": "agent_1"}},
    )
    agents = AgentsResource(api)  # type: ignore[arg-type]
    guardrails = GuardrailsResource(api)  # type: ignore[arg-type]

    agents.set_guardrails("agent_1", ["guardrail_1"])
    guardrails.set_agent_guardrails("agent_1", ["guardrail_1"])

    expected = (
        "PUT", "/agents/agent_1/guardrails", {"guardrailSetIds": ["guardrail_1"]},
    )
    assert api.calls[0] == expected
    assert api.calls[1] == expected


def test_canonical_organization_ownership_and_member_profile_lookups() -> None:
    api = RecordingClient()
    api.queue(
        "POST",
        {"profiles": []},
        {"data": {"id": "org_1"}},
        {"profiles": []},
    )
    organizations = OrganizationsResource(api)  # type: ignore[arg-type]
    teams = TeamsResource(api)  # type: ignore[arg-type]
    authorization = AuthorizationResource(api)  # type: ignore[arg-type]

    organizations.lookup_member_profiles(
        "org/one",
        ["user_1"],
        members=[{"userId": "user_1"}],
        emails=["jan@example.test"],
    )
    organizations.transfer_ownership("org/one", "member/one")
    teams.lookup_member_profiles("team/one", emails=["jan@example.test"])
    authorization.delete_delegation("delegation/one", reason="No longer needed")

    assert api.calls[0] == (
        "POST",
        "/organizations/org%2Fone/member-profiles/lookup",
        {
            "members": [{"userId": "user_1"}],
            "userIds": ["user_1"],
            "emails": ["jan@example.test"],
        },
    )
    assert api.calls[1] == (
        "POST",
        "/organizations/org%2Fone/transfer-ownership",
        {"memberId": "member/one"},
    )
    assert api.calls[2] == (
        "POST",
        "/teams/team%2Fone/member-profiles/lookup",
        {"emails": ["jan@example.test"]},
    )
    assert api.calls[3] == (
        "DELETE",
        "/authorization/delegations/delegation%2Fone",
        {"reason": "No longer needed"},
    )


def test_canonical_evaluation_targets_and_source_asset_lease_credentials() -> None:
    api = RecordingClient()
    api.queue("POST", {"run": {"id": "run_1"}}, {"staged": True})
    evaluations = EvaluationsResource(api)  # type: ignore[arg-type]

    evaluations.run(
        "evaluation/one",
        run_id="run_1",
        target={
            "kind": "function",
            "id": "server_1",
            "versionId": "version_2",
            "invocation": {"method": "POST", "path": "/score"},
        },
        purpose="release",
    )
    evaluations.stage_source_asset(
        "run/one",
        "asset/one",
        case_id="case_1",
        execution_lease={"owner": "worker_1", "token": "lease_secret"},
    )

    assert api.calls[0] == (
        "POST",
        "/evaluations/evaluation%2Fone/runs",
        {
            "purpose": "release",
            "id": "run_1",
            "target": {
                "kind": "function",
                "id": "server_1",
                "versionId": "version_2",
                "invocation": {"method": "POST", "path": "/score"},
            },
        },
    )
    assert api.calls[1] == (
        "POST",
        "/evaluations/runs/run%2Fone/source-assets/asset%2Fone/stage",
        {"caseId": "case_1", "executionLease": {"owner": "worker_1", "token": "lease_secret"}},
    )


def test_current_deployment_guardrail_and_version_publication_payloads() -> None:
    api = RecordingClient()
    api.queue(
        "POST",
        {"deployment": {"id": "deployment_1"}},
        {"guardrail": {"id": "guardrail_1"}},
        {"guardrail": {"id": "guardrail_1"}},
    )
    resources = ResourcesResource(api)  # type: ignore[arg-type]
    guardrails = GuardrailsResource(api)  # type: ignore[arg-type]
    policy = {
        "schemaVersion": "computer_agents_guardrail_policy_v1",
        "rules": [{
            "id": "restrict-export",
            "match": {"actionClasses": ["secret_export"]},
            "outcome": "deny",
            "severity": "critical",
            "recommendedControl": "deny_effect",
            "obligations": ["security_review"],
        }],
    }

    resources.deploy("server_1", release_id="release_1")
    guardrails.create(name="Release policy", policy=policy)
    guardrails.publish_version(
        "guardrail_1",
        "version_1",
        snapshot={
            "schemaVersion": "computer_agents_guardrail_v2",
            "name": "Release policy",
            "policy": policy,
        },
    )

    assert api.calls[0] == ("POST", "/servers/server_1/deploy", {"releaseId": "release_1"})
    assert api.calls[1] == ("POST", "/guardrails", {"name": "Release policy", "policy": policy})
    assert api.calls[2] == (
        "POST",
        "/guardrails/guardrail_1/versions/version_1/publish",
        {
            "snapshot": {
                "schemaVersion": "computer_agents_guardrail_v2",
                "name": "Release policy",
                "policy": policy,
            },
        },
    )


def test_new_project_context_and_publication_payloads_are_forwarded() -> None:
    api = RecordingClient()
    api.queue(
        "POST",
        {"success": True},
        {"deployment": {"id": "deployment_1"}},
        {"update": {"id": "update_1"}},
        {"thread": {"id": "thread_1"}},
        {"data": {"id": "metronome_1"}},
        {"data": {"id": "metronome_1"}},
        {"data": {"run": {"id": "run_1"}}},
        {"testPlan": {"id": "test_plan_1"}},
    )
    api.queue("PATCH", {"thread": {"id": "thread_1"}})
    git = GitResource(api)  # type: ignore[arg-type]
    resources = ResourcesResource(api)  # type: ignore[arg-type]
    projects = ProjectsResource(api)  # type: ignore[arg-type]
    threads = ThreadsResource(api)  # type: ignore[arg-type]
    metronomes = MetronomesResource(api)  # type: ignore[arg-type]
    tests = PlansResource(api)  # type: ignore[arg-type]
    definition: dict[str, Any] = {"nodes": [], "edges": []}

    git.prepare_github(
        "env_1",
        repo_full_name="computer-agents/sdk",
        branch="release",
        project_id="project_1",
    )
    resources.deploy(
        "server_1",
        project_delivery_promotion_id="promotion_1",
        project_delivery_resource_candidate_id="candidate_1",
    )
    projects.create_update(
        "project_1",
        "Release candidate ready",
        kind="comment",
        status="on_track",
    )
    threads.create(
        content="Validate release",
        enabled_skills=["release"],
        reasoning_effort="high",
        env_vars={"RELEASE_CHANNEL": "next"},
        message_metadata={"source": "sdk"},
    )
    threads.update(
        "thread_1",
        environment_id="env_2",
        app_id="runner",
        task="Publish SDKs",
        metadata={"release": True},
    )
    metronomes.publish(
        "metronome_1",
        version_id="version_1",
        definition=definition,
        description="Release workflow",
    )
    metronomes.publish_version(
        "metronome_1",
        "version_1",
        snapshot={"name": "Release workflow", "definition": definition},
    )
    metronomes.test_trigger(
        "metronome_1",
        payload={"ref": "main"},
        source_event_id="event_1",
        summary="Release smoke test",
    )
    tests.create(
        name="SDK release",
        cases=[{"id": "case_1", "name": "Smoke", "command": "pytest"}],
        publish_initial_version=False,
    )

    assert api.calls[0] == (
        "POST",
        "/environments/env_1/github/prepare",
        {"repoFullName": "computer-agents/sdk", "branch": "release", "projectId": "project_1"},
    )
    assert api.calls[1] == (
        "POST",
        "/servers/server_1/deploy",
        {
            "projectDeliveryPromotionId": "promotion_1",
            "projectDeliveryResourceCandidateId": "candidate_1",
        },
    )
    assert api.calls[2] == (
        "POST",
        "/projects/project_1/updates",
        {"body": "Release candidate ready", "kind": "comment", "status": "on_track"},
    )
    assert api.calls[3] == (
        "POST",
        "/threads",
        {
            "content": "Validate release",
            "messageMetadata": {"source": "sdk"},
            "enabledSkills": ["release"],
            "reasoningEffort": "high",
            "envVars": {"RELEASE_CHANNEL": "next"},
            "stream": False,
        },
    )
    assert api.calls[4] == (
        "PATCH",
        "/threads/thread_1",
        {
            "environmentId": "env_2",
            "appId": "runner",
            "task": "Publish SDKs",
            "metadata": {"release": True},
        },
    )
    assert api.calls[5] == (
        "POST",
        "/metronomes/metronome_1/publish",
        {
            "active": True,
            "versionId": "version_1",
            "definition": definition,
            "description": "Release workflow",
        },
    )
    assert api.calls[6] == (
        "POST",
        "/metronomes/metronome_1/versions/version_1/publish",
        {"snapshot": {"name": "Release workflow", "definition": definition}},
    )
    assert api.calls[7] == (
        "POST",
        "/metronomes/metronome_1/triggers/test",
        {
            "triggerType": "manual_test",
            "payload": {"ref": "main"},
            "sourceEventId": "event_1",
            "summary": "Release smoke test",
        },
    )
    assert api.calls[8] == (
        "POST",
        "/test-plans",
        {
            "name": "SDK release",
            "cases": [{"id": "case_1", "name": "Smoke", "command": "pytest"}],
            "publishInitialVersion": False,
        },
    )
