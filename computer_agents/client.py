"""ComputerAgentsClient - The Official Computer Agents Python SDK.

A clean, simple SDK for interacting with the Computer Agents Cloud API.
Provides typed access to all API resources with streaming support.

Example::

    from computer_agents import ComputerAgentsClient

    client = ComputerAgentsClient(api_key="ca_...")

    # Execute a task (simplest usage)
    result = client.run(
        "Create a REST API with Flask",
        environment_id="env_xxx",
        on_event=lambda e: print(e["type"]),
    )
    print(result.content)

    # Or use the thread API for multi-turn conversations
    thread = client.threads.create(environment_id="env_xxx")
    result = client.threads.send_message(
        thread["id"],
        content="Create a REST API",
        on_event=lambda e: print(e),
    )
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any, Callable

from ._api_client import ApiClient
from .resources import (
    AgentsResource,
    BillingResource,
    BudgetResource,
    EnvironmentsResource,
    FilesResource,
    GitResource,
    OrchestrationsResource,
    ProjectsResource,
    RunsResource,
    SchedulesResource,
    SendMessageResult,
    ThreadsResource,
    TriggersResource,
)
from .types import Environment, HealthCheck, Metrics, Project


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
    - ``environments`` -- Environment configuration and container lifecycle
    - ``agents`` -- Agent configuration
    - ``files`` -- File management in environment workspaces
    - ``schedules`` -- Scheduled task management
    - ``triggers`` -- Event-driven triggers
    - ``orchestrations`` -- Agent-to-agent orchestration
    - ``budget`` -- Budget and usage tracking
    - ``billing`` -- Billing records and statistics
    - ``git`` -- Git operations on workspaces

    For simple use cases, use the :meth:`run` method which handles thread
    creation and streaming automatically.

    Args:
        api_key: API key for authentication. Falls back to
            ``COMPUTER_AGENTS_API_KEY`` environment variable.
        base_url: Base URL for the API. Defaults to
            ``https://api.computer-agents.com``.
        timeout: Request timeout in seconds. Defaults to 60.
        debug: Enable debug logging. Defaults to False.
    """

    def __init__(
        self,
        api_key: str | None = None,
        *,
        base_url: str | None = None,
        timeout: float | None = None,
        debug: bool = False,
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
        )

        # Initialize all resource managers
        self.threads = ThreadsResource(self.api)
        self.environments = EnvironmentsResource(self.api)
        self.agents = AgentsResource(self.api)
        self.files = FilesResource(self.api)
        self.schedules = SchedulesResource(self.api)
        self.triggers = TriggersResource(self.api)
        self.orchestrations = OrchestrationsResource(self.api)
        self.budget = BudgetResource(self.api)
        self.billing = BillingResource(self.api)
        self.git = GitResource(self.api)
        self.runs = RunsResource(self.api)
        self.projects = ProjectsResource(self.api)

    def close(self) -> None:
        """Close the underlying HTTP client."""
        self.api.close()

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
        environment_id: str,
        *,
        thread_id: str | None = None,
        agent_config: dict[str, Any] | None = None,
        on_event: Callable[[dict[str, Any]], None] | None = None,
        timeout: float | None = None,
    ) -> RunResult:
        """Execute a task with automatic thread management.

        This is the simplest way to run an agent task. It handles:
        - Creating a thread (if ``thread_id`` not provided)
        - Sending the message with SSE streaming
        - Returning the result with thread ID for follow-ups

        Args:
            task: The task to execute (e.g. ``"Create a REST API with Flask"``).
            environment_id: Environment ID to execute in.
            thread_id: Thread ID to continue (optional).
            agent_config: Agent configuration override (model, instructions, etc.).
            on_event: Callback for streaming events.
            timeout: Execution timeout in seconds.

        Returns:
            :class:`RunResult` with ``content``, ``thread_id``, and ``run``.

        Example::

            # Simple one-shot execution
            result = client.run("Create hello.py", environment_id="env_xxx")
            print(result.content)

            # With streaming progress
            result = client.run(
                "Build a REST API",
                environment_id="env_xxx",
                on_event=lambda e: print(e.get("type")),
            )

            # Continue the conversation
            follow_up = client.run(
                "Add authentication",
                environment_id="env_xxx",
                thread_id=result.thread_id,
            )
        """
        # Create or reuse thread
        if thread_id is None:
            thread = self.threads.create(environment_id=environment_id)
            thread_id = thread["id"]

        # Send message and stream response
        result = self.threads.send_message(
            thread_id,
            content=task,
            agent_config=agent_config,
            on_event=on_event,
            timeout=timeout,
        )

        return RunResult(
            content=result.content,
            thread_id=thread_id,
            run=result.run,
        )

    def quick_setup(
        self,
        *,
        internet_access: bool = True,
        environment_name: str | None = None,
    ) -> dict[str, Any]:
        """Quick setup with default environment.

        Creates a default environment if none exists, returning both
        the project and environment ready for execution.

        Returns:
            Dict with ``project`` and ``environment`` keys.

        Example::

            setup = client.quick_setup(internet_access=True)
            result = client.run(
                "Hello world!",
                environment_id=setup["environment"]["id"],
            )
        """
        project = self.projects.get()

        environments = self.environments.list()
        default_env = next((e for e in environments if e.get("isDefault")), None)

        if default_env is None:
            default_env = self.environments.create(
                name=environment_name or "default",
                internet_access=internet_access,
                is_default=True,
            )

        return {"project": project, "environment": default_env}

    # =========================================================================
    # Health & Monitoring
    # =========================================================================

    def health(self) -> HealthCheck:
        """Check API health status."""
        return self.api.get("/health")

    def metrics(self) -> Metrics:
        """Get API metrics."""
        return self.api.get("/metrics")

    @property
    def base_url(self) -> str:
        """Get API base URL."""
        return self.api.base_url
