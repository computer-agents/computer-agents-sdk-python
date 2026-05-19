"""Official Python SDK for Computer Agents.

Run agents, manage persistent cloud computers and projects, and operate deployable
resources such as web apps, functions, databases, auth modules, agent runtimes,
and secret vaults.

Example::

    from computer_agents import ComputerAgentsClient

    client = ComputerAgentsClient(api_key="ca_...")

    # Execute a task
    result = client.run(
        "Create a REST API",
        computer_id="env_xxx",
        on_event=lambda e: print(e["type"]),
    )
    print(result.content)
"""

__version__ = "2.6.3"

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
    AgentRuntimesResource,
    AgentsResource,
    AuthResource,
    BillingResource,
    BudgetResource,
    ComputersResource,
    DatabasesResource,
    EnvironmentsResource,
    FilesResource,
    FunctionsResource,
    GitResource,
    NotificationsResource,
    OrchestrationsResource,
    ProjectsResource,
    ResourcesResource,
    RuntimesResource,
    SchedulesResource,
    SendMessageResult,
    SecretsResource,
    SkillsResource,
    TasksResource,
    ThreadsResource,
    TriggersResource,
    WebAppsResource,
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
    ProjectSummary,
    ProjectListParams,
    ProjectListResult,
    ProjectDetailResult,

    # Environments
    Environment,
    Computer,
    CreateEnvironmentParams,
    CreateComputerParams,
    UpdateEnvironmentParams,
    UpdateComputerParams,
    EnvironmentComputeProfileId,
    EnvironmentComputeResources,
    EnvironmentPricingMetadata,
    EnvironmentMetadata,
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
    EnvironmentSnapshot,
    EnvironmentChangeKind,
    EnvironmentChangeOperation,
    EnvironmentChangeSourceKind,
    EnvironmentChangeFileRecord,
    EnvironmentChangeEntry,
    EnvironmentChangeListResponse,
    SnapshotFileEntry,
    EnvironmentSnapshotFilesResponse,
    EnvironmentSnapshotDiffResponse,
    EnvironmentSnapshotFileResponse,
    EnvironmentForkFromSnapshotResponse,
    EnvironmentSnapshot,
    EnvironmentChangeKind,
    EnvironmentChangeOperation,
    EnvironmentChangeSourceKind,
    EnvironmentChangeFileRecord,
    EnvironmentChangeEntry,
    EnvironmentChangeListResponse,
    SnapshotFileEntry,
    EnvironmentSnapshotFilesResponse,
    EnvironmentSnapshotDiffResponse,
    EnvironmentSnapshotFileResponse,
    EnvironmentForkFromSnapshotResponse,

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
    ThreadFeedbackRating,
    ThreadFeedbackReportType,
    ThreadFeedbackSummary,
    ThreadFeedbackReportCreate,
    ThreadFeedbackReport,
    ThreadPermissionRequest,
    ThreadPermissionDecisionParams,
    ThreadPermissionDecisionResponse,

    # Tasks
    Task,
    TaskStatus,
    TaskPriority,
    TaskType,
    TaskCommentAuthorType,
    TaskSprintStatus,
    TaskReleaseStatus,
    TaskListParams,
    CreateTaskParams,
    UpdateTaskParams,
    TaskListResult,
    TaskDetails,
    TaskDetailResult,
    TaskComment,
    TaskCommentCreateParams,
    TaskCommentListParams,
    TaskCommentListResult,
    TaskSprint,
    TaskSprintCreateParams,
    TaskSprintUpdateParams,
    TaskSprintListParams,
    TaskSprintListResult,
    TaskSprintDetailResult,
    TaskRelease,
    TaskReleaseCreateParams,
    TaskReleaseUpdateParams,
    TaskReleaseListParams,
    TaskReleaseListResult,
    TaskReleaseDetailResult,
    TaskWorkspaceParams,
    TaskWorkspaceResult,
    TaskStartThreadParams,
    TaskStartThreadResult,
    TaskRunThreadParams,
    TaskRunThreadResult,

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
    BuiltinAgentModel,
    PermissionAccessLevel,
    PermissionResourceType,
    PermissionSetSubjectType,
    PermissionRule,
    PermissionResourcePolicy,
    PermissionSet,

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
    InAppNotification,
    PushTokenRegistration,
    PushTokenRegistrationResponse,
    PushTokenDeleteResponse,
    PushTokenDescriptor,

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
    "AgentRuntimesResource",
    "AgentsResource",
    "AuthResource",
    "BillingResource",
    "BudgetResource",
    "ComputersResource",
    "DatabasesResource",
    "EnvironmentsResource",
    "Computer",
    "FilesResource",
    "FunctionsResource",
    "GitResource",
    "NotificationsResource",
    "OrchestrationsResource",
    "ProjectsResource",
    "ResourcesResource",
    "RuntimesResource",
    "SchedulesResource",
    "SendMessageResult",
    "SecretsResource",
    "SkillsResource",
    "TasksResource",
    "ThreadsResource",
    "TriggersResource",
    "WebAppsResource",

    # Environment history types
    "EnvironmentSnapshot",
    "EnvironmentChangeKind",
    "EnvironmentChangeOperation",
    "EnvironmentChangeSourceKind",
    "EnvironmentChangeFileRecord",
    "EnvironmentChangeEntry",
    "EnvironmentChangeListResponse",
    "SnapshotFileEntry",
    "EnvironmentSnapshotFilesResponse",
    "EnvironmentSnapshotDiffResponse",
    "EnvironmentSnapshotFileResponse",
    "EnvironmentForkFromSnapshotResponse",
    "PermissionAccessLevel",
    "PermissionResourceType",
    "PermissionSetSubjectType",
    "PermissionRule",
    "PermissionResourcePolicy",
    "PermissionSet",
    "ProjectSummary",
    "ProjectListParams",
    "ProjectListResult",
    "ProjectDetailResult",
    "ThreadFeedbackRating",
    "ThreadFeedbackReportType",
    "ThreadFeedbackSummary",
    "ThreadFeedbackReportCreate",
    "ThreadFeedbackReport",
    "ThreadPermissionRequest",
    "ThreadPermissionDecisionParams",
    "ThreadPermissionDecisionResponse",
    "Task",
    "TaskStatus",
    "TaskPriority",
    "TaskType",
    "TaskCommentAuthorType",
    "TaskSprintStatus",
    "TaskReleaseStatus",
    "TaskListParams",
    "CreateTaskParams",
    "UpdateTaskParams",
    "TaskListResult",
    "TaskDetails",
    "TaskDetailResult",
    "TaskComment",
    "TaskCommentCreateParams",
    "TaskCommentListParams",
    "TaskCommentListResult",
    "TaskSprint",
    "TaskSprintCreateParams",
    "TaskSprintUpdateParams",
    "TaskSprintListParams",
    "TaskSprintListResult",
    "TaskSprintDetailResult",
    "TaskRelease",
    "TaskReleaseCreateParams",
    "TaskReleaseUpdateParams",
    "TaskReleaseListParams",
    "TaskReleaseListResult",
    "TaskReleaseDetailResult",
    "TaskWorkspaceParams",
    "TaskWorkspaceResult",
    "TaskStartThreadParams",
    "TaskStartThreadResult",
    "TaskRunThreadParams",
    "TaskRunThreadResult",
    "InAppNotification",
    "PushTokenRegistration",
    "PushTokenRegistrationResponse",
    "PushTokenDeleteResponse",
    "PushTokenDescriptor",
]
