"""ComputerAgentsClient - The Official Computer Agents Python SDK.

A clean, simple SDK for interacting with the Computer Agents Cloud API.
Provides typed access to all API resources with streaming support.

Example::

    from computer_agents import ComputerAgentsClient

    client = ComputerAgentsClient()

    # Execute a task — that's it. No setup needed.
    result = client.run("Create a REST API with Flask")
    print(result.content)

    # With streaming events
    result = client.run(
        "Build a web scraper",
        on_event=lambda e: print(e["type"]),
    )

    # Continue the conversation
    follow_up = client.run("Add error handling", thread_id=result.thread_id)
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any, Callable, cast

from ._api_client import ApiClient
from .resources import (
    AgentRuntimesResource,
    AccountResource,
    AgentsResource,
    ApiKeysResource,
    AssuranceResource,
    AttachmentsResource,
    AuthResource,
    AuthorizationResource,
    BillingResource,
    BudgetResource,
    BatchesResource,
    DatabasesResource,
    EvaluationsResource,
    EmailResource,
    EnvironmentsResource,
    EvidenceResource,
    FilesResource,
    FineTuningResource,
    FunctionsResource,
    GitResource,
    GuardrailsResource,
    IdentityConnectionsResource,
    KnowledgeResource,
    LocalBridgeResource,
    MetronomesResource,
    NotificationsResource,
    OrganizationsResource,
    OrchestrationsResource,
    ProjectsResource,
    OptimizationCampaignsResource,
    OptimizationCandidatesResource,
    PromptsResource,
    ReleaseControlResource,
    ReportsResource,
    ResourcesResource,
    SchedulesResource,
    SecurityResource,
    SecretsResource,
    SkillsResource,
    TasksResource,
    TeamsResource,
    TestsResource,
    ThreadsResource,
    TriggersResource,
    SystemResource,
    VoiceAgentsResource,
    WebAppsResource,
)
from .types import HealthCheck, Metrics


@dataclass
class RunResult:
    """Result from the :meth:`ComputerAgentsClient.run` method."""

    content: str
    """The final response content."""

    thread_id: str
    """The thread ID (for continuing conversations)."""

    run: dict[str, Any] | None = None
    """Run details if available."""


class ComputerAgentsClient:
    """Complete SDK for the Computer Agents Cloud API.

    This is the main entry point for the SDK. It provides access to all API
    resources through typed methods:

    - ``threads`` -- Conversation management with SSE streaming
    - ``tasks`` -- Planning tasks, comments, releases, sprints, and task threads
    - ``environments`` / ``computers`` -- Computer configuration and lifecycle
    - ``resources`` -- Web apps, functions, auth modules, runtimes, and secrets
    - Product-shaped managers: ``web_apps``, ``functions``, ``auth``,
      ``runtimes``, and ``secrets``
    - ``databases`` -- Managed database surfaces
    - ``agents`` / ``prompts`` / ``skills`` / ``knowledge`` -- Agent building blocks
    - ``guardrails`` -- Reusable invisible prompt adaptation sets
    - ``evaluations`` -- Versioned evaluation datasets and runs
    - ``tests`` -- Deterministic test plans, runs, and evidence
    - ``assurance`` -- Evidence-bound release policies and decisions
    - ``fine_tuning`` -- Jobs that improve agents from evaluation sets
    - ``optimization_campaigns`` / ``optimization_candidates`` -- Optimization
    - ``release_control`` -- Evidence-gated release execution
    - ``files`` -- File management in computer workspaces
    - ``schedules`` / ``triggers`` / ``orchestrations`` -- Automation controls
    - ``metronomes`` -- Agentic workflow automations
    - ``batches`` -- Durable, capacity-aware workload queue
    - ``security`` / ``evidence`` -- Security Agents and evidence review
    - ``organizations`` / ``teams`` / ``authorization`` -- Tenant access control
    - ``identity_connections`` -- Enterprise identity connection management
    - ``budget`` / ``billing`` -- Billing, managed inference, and cost analytics
    - ``api_keys`` / ``account`` -- Authentication and account data controls
    - ``voice_agents`` / ``notifications`` / ``email`` / ``attachments`` -- Communications
    - ``local_bridge`` -- Local appliance and workspace synchronization
    - ``reports`` / ``system`` -- Reports and deployment discovery
    - ``git`` -- Git operations on computers (compatibility helper)

    For simple use cases, use the :meth:`run` method which handles thread
    creation and streaming automatically.

    Args:
        api_key: API key for authentication. Falls back to
            ``COMPUTER_AGENTS_API_KEY`` environment variable.
        base_url: Base URL for the API. Defaults to
            ``COMPUTER_AGENTS_BASE_URL``, then ``COMPUTER_AGENTS_API_URL``,
            then ``https://api.computer-agents.com``.
        timeout: Request timeout in seconds. Defaults to 60.
        debug: Enable debug logging. Defaults to False.
        organization_id: Active organization for tenant-scoped API calls.
    """

    def __init__(
        self,
        api_key: str | None = None,
        *,
        base_url: str | None = None,
        timeout: float | None = None,
        debug: bool = False,
        organization_id: str | None = None,
    ) -> None:
        resolved_key = (
            api_key
            or os.environ.get("COMPUTER_AGENTS_API_KEY")
            or os.environ.get("TESTBASE_API_KEY")
        )

        if not resolved_key:
            raise ValueError(
                "ComputerAgentsClient requires an API key. Provide it via:\n"
                '1. Constructor: ComputerAgentsClient(api_key="...")\n'
                "2. Environment variable: COMPUTER_AGENTS_API_KEY"
            )

        self.api = ApiClient(
            api_key=resolved_key,
            base_url=base_url,
            timeout=timeout,
            debug=debug,
            organization_id=organization_id,
        )

        # Initialize all resource managers
        self.threads = ThreadsResource(self.api)
        self.tasks = TasksResource(self.api)
        self.environments = EnvironmentsResource(self.api)
        self.computers = self.environments
        self.agents = AgentsResource(self.api)
        self.prompts = PromptsResource(self.api)
        self.guardrails = GuardrailsResource(self.api)
        self.knowledge = KnowledgeResource(self.api)
        self.evaluations = EvaluationsResource(self.api)
        self.tests = TestsResource(self.api)
        self.assurance = AssuranceResource(self.api)
        self.fine_tuning = FineTuningResource(self.api)
        self.resources = ResourcesResource(self.api)
        self.evidence = EvidenceResource(self.api)
        self.web_apps = WebAppsResource(self.api)
        self.functions = FunctionsResource(self.api)
        self.auth = AuthResource(self.api)
        self.runtimes = AgentRuntimesResource(self.api)
        self.agent_runtimes = self.runtimes
        self.secrets = SecretsResource(self.api)
        self.databases = DatabasesResource(self.api)
        self.skills = SkillsResource(self.api)
        self.files = FilesResource(self.api)
        self.schedules = SchedulesResource(self.api)
        self.triggers = TriggersResource(self.api)
        self.metronomes = MetronomesResource(self.api)
        self.batches = BatchesResource(self.api)
        self.orchestrations = OrchestrationsResource(self.api)
        self.budget = BudgetResource(self.api)
        self.billing = BillingResource(self.api)
        self.git = GitResource(self.api)
        self.notifications = NotificationsResource(self.api)
        self.organizations = OrganizationsResource(self.api)
        self.teams = TeamsResource(self.api)
        self.authorization = AuthorizationResource(self.api)
        self.identity_connections = IdentityConnectionsResource(self.api)
        self.local_bridge = LocalBridgeResource(self.api)
        self.projects = ProjectsResource(self.api)
        self.optimization_campaigns = OptimizationCampaignsResource(self.api)
        self.optimization_candidates = OptimizationCandidatesResource(self.api)
        self.release_control = ReleaseControlResource(self.api)
        self.security = SecurityResource(self.api)
        self.voice_agents = VoiceAgentsResource(self.api)
        self.api_keys = ApiKeysResource(self.api)
        self.account = AccountResource(self.api)
        self.reports = ReportsResource(self.api)
        self.email = EmailResource(self.api)
        self.attachments = AttachmentsResource(self.api)
        self.system = SystemResource(self.api)

        # Cached default environment (populated on first run without environment_id)
        self._default_environment_id: str | None = None

    def close(self) -> None:
        """Close the underlying HTTP client."""
        self.api.close()

    def with_organization(self, organization_id: str) -> "ComputerAgentsClient":
        """Return a client scoped to another organization on the same deployment."""
        return ComputerAgentsClient(
            api_key=self.api.api_key,
            base_url=self.api.base_url,
            timeout=self.api.timeout,
            debug=self.api.debug,
            organization_id=organization_id,
        )

    def __enter__(self) -> "ComputerAgentsClient":
        return self

    def __exit__(self, *args: Any) -> None:
        self.close()

    # =========================================================================
    # High-Level Convenience Methods
    # =========================================================================

    def run(
        self,
        task: str,
        environment_id: str | None = None,
        *,
        computer_id: str | None = None,
        thread_id: str | None = None,
        agent_id: str | None = None,
        reasoning_effort: str | None = None,
        queue_when_capacity_unavailable: bool | None = None,
        knowledge_context: dict[str, Any] | None = None,
        idempotency_key: str | None = None,
        on_event: Callable[[dict[str, Any]], None] | None = None,
        timeout: float | None = None,
    ) -> RunResult:
        """Execute a task with automatic thread management.

        This is the simplest way to run an agent task. It handles:
        - Auto-creating a default environment (if ``environment_id`` not provided)
        - Creating a thread (if ``thread_id`` not provided)
        - Sending the message with SSE streaming
        - Returning the result with thread ID for follow-ups

        Args:
            task: The task to execute (e.g. ``"Create a REST API with Flask"``).
            environment_id: Environment ID to execute in. If not provided,
                a default environment is created automatically.
            thread_id: Thread ID to continue (optional).
            agent_id: Agent to bind when a new thread is created.
            reasoning_effort: Per-turn reasoning effort.
            queue_when_capacity_unavailable: Durably queue when runtime capacity is full.
            knowledge_context: Knowledge libraries and immutable versions for the turn.
            idempotency_key: Stable retry identity for this exact message.
            on_event: Callback for streaming events.
            timeout: Execution timeout in seconds.

        Returns:
            :class:`RunResult` with ``content``, ``thread_id``, and ``run``.

        Example::

            # Simplest usage — no setup needed
            result = client.run("Create hello.py")
            print(result.content)

            # With streaming progress
            result = client.run(
                "Build a REST API",
                on_event=lambda e: print(e.get("type")),
            )

            # Continue the conversation
            follow_up = client.run(
                "Add authentication",
                thread_id=result.thread_id,
            )

            # Explicit environment
            result = client.run("Deploy to prod", environment_id="env_xxx")
        """
        # Auto-resolve environment/computer if not provided
        environment_id = computer_id or environment_id
        if environment_id is None:
            environment_id = self._ensure_default_environment()

        # Create or reuse thread
        if thread_id is None:
            thread = self.threads.create(environment_id=environment_id, agent_id=agent_id)
            thread_id = thread["id"]

        # Send message and stream response
        result = self.threads.send_message(
            thread_id,
            content=task,
            reasoning_effort=reasoning_effort,
            queue_when_capacity_unavailable=queue_when_capacity_unavailable,
            knowledge_context=knowledge_context,
            idempotency_key=idempotency_key,
            on_event=on_event,
            timeout=timeout,
        )

        return RunResult(
            content=result.content,
            thread_id=thread_id,
            run=result.run,
        )

    def _ensure_default_environment(self) -> str:
        """Return the cached default environment ID, creating one if needed."""
        if self._default_environment_id is not None:
            return self._default_environment_id

        environments = self.environments.list()
        default_env = next((e for e in environments if e.get("isDefault")), None)

        if default_env is None:
            default_env = self.environments.create(
                name="default",
                internet_access=True,
                is_default=True,
            )

        self._default_environment_id = default_env["id"]
        return self._default_environment_id

    def quick_setup(
        self,
        *,
        project_id: str | None = None,
        internet_access: bool = True,
        environment_name: str | None = None,
        computer_name: str | None = None,
    ) -> dict[str, Any]:
        """Quick setup with default environment.

        Creates a default environment if none exists, returning both
        the project and environment ready for execution.

        .. note::
            You usually don't need to call this directly. ``run()`` auto-creates
            a default environment when ``environment_id`` is omitted.

        Returns:
            Dict with ``project``, ``environment``, and ``computer`` keys.

        Example::

            setup = client.quick_setup(internet_access=True)
            env_id = setup["environment"]["id"]
        """
        project = self.projects.get(project_id)

        environments = self.environments.list()
        default_env = next((e for e in environments if e.get("isDefault")), None)

        if default_env is None:
            default_env = self.environments.create(
                name=computer_name or environment_name or "default",
                internet_access=internet_access,
                is_default=True,
            )

        return {"project": project, "environment": default_env, "computer": default_env}

    # =========================================================================
    # Health & Monitoring
    # =========================================================================

    def health(self) -> HealthCheck:
        """Check API health status."""
        return cast(HealthCheck, self.api.get("/health"))

    def ready(self) -> dict[str, Any]:
        """Check whether the API and its required dependencies are ready."""
        return cast(dict[str, Any], self.api.get("/ready"))

    def metrics(self) -> Metrics:
        """Get API metrics."""
        return cast(Metrics, self.api.get("/metrics"))

    @property
    def base_url(self) -> str:
        """Get API base URL."""
        return self.api.base_url
