"""Computer Agents SDK - Official Python client for the Computer Agents Cloud API.

Execute Claude-powered AI agents in isolated cloud containers.

Example::

    from computer_agents import ComputerAgentsClient

    client = ComputerAgentsClient(api_key="ca_...")

    # Execute a task
    result = client.run(
        "Create a REST API",
        environment_id="env_xxx",
        on_event=lambda e: print(e["type"]),
    )
    print(result.content)
"""

__version__ = "2.2.0"

# ============================================================================
# Main Client
# ============================================================================

from .client import ComputerAgentsClient, RunResult
from ._exceptions import ApiClientError
from ._api_client import ApiClient

# ============================================================================
# Resource Managers (for advanced usage)
# ============================================================================

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

# ============================================================================
# Types
# ============================================================================

from .types import (
    # Common
    PaginationParams,
    ApiErrorBody,

    # Projects
    Project,
    CreateProjectParams,
    UpdateProjectParams,
    ProjectStats,

    # Environments
    Environment,
    CreateEnvironmentParams,
    UpdateEnvironmentParams,
    EnvironmentVariable,
    McpServer,
    RuntimeConfig,
    PackagesConfig,
    AvailableRuntimes,
    ContainerStatus,
    BuildResult,
    BuildStatusResult,
    BuildLogsResult,
    TestBuildResult,
    DockerfileResult,
    ValidateDockerfileResult,
    InstallPackagesResult,
    StartContainerParams,
    StartContainerResult,

    # Threads
    Thread,
    CreateThreadParams,
    UpdateThreadParams,
    ListThreadsParams,
    SendMessageParams,
    ThreadMessage,
    AgentConfig,
    CopyThreadParams,
    SearchThreadsParams,
    SearchThreadResult,
    SearchThreadsResponse,
    ThreadLogEntry,
    ResearchSession,

    # Stream Events
    StreamEvent,
    MessageStreamEvent,
    ResponseStartedEvent,
    ResponseItemCompletedEvent,
    ResponseCompletedEvent,
    StreamCompletedEvent,
    StreamErrorEvent,

    # Runs
    Run,
    CreateRunParams,
    UpdateRunParams,
    ListRunsParams,
    RunLogEntry,
    RunDiff,
    TokenUsage,

    # Agents
    CloudAgent,
    CreateAgentParams,
    UpdateAgentParams,
    AgentBinary,

    # Budget & Billing
    BudgetStatus,
    CanExecuteResult,
    IncreaseBudgetParams,
    IncreaseBudgetResult,
    BillingRecord,
    ListBillingRecordsParams,
    BillingAccount,
    UsageStats,
    UsageStatsParams,

    # Files
    FileEntry,
    ListFilesParams,
    UploadFileParams,
    CreateDirectoryParams,

    # Git
    GitDiffFile,
    GitDiffResult,
    GitCommitParams,
    GitCommitResult,
    GitPushParams,
    GitPushResult,

    # Schedules
    Schedule,
    CreateScheduleParams,
    UpdateScheduleParams,

    # Triggers
    Trigger,
    CreateTriggerParams,
    UpdateTriggerParams,
    TriggerAction,
    TriggerExecution,

    # Orchestrations
    Orchestration,
    CreateOrchestrationParams,
    UpdateOrchestrationParams,
    OrchestrationStep,
    OrchestrationStepResult,
    OrchestrationRun,

    # Health
    HealthCheck,
    Metrics,
)

__all__ = [
    # Version
    "__version__",

    # Client
    "ComputerAgentsClient",
    "RunResult",
    "ApiClientError",
    "ApiClient",

    # Resources
    "AgentsResource",
    "BillingResource",
    "BudgetResource",
    "EnvironmentsResource",
    "FilesResource",
    "GitResource",
    "OrchestrationsResource",
    "ProjectsResource",
    "RunsResource",
    "SchedulesResource",
    "SendMessageResult",
    "ThreadsResource",
    "TriggersResource",
]
