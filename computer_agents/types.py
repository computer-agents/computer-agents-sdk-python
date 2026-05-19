"""Type definitions for the Computer Agents Cloud API.

These types mirror the TypeScript SDK types exactly, using Python
conventions (snake_case, TypedDict, Literal).
"""

from __future__ import annotations

from typing import Any, Dict, List, Literal, Optional, TypedDict, Union


# ============================================================================
# Common Types
# ============================================================================

class PaginationParams(TypedDict, total=False):
    limit: int
    offset: int


class Pagination(TypedDict):
    total: int
    limit: int
    offset: int


class ApiErrorBody(TypedDict, total=False):
    error: str
    message: str
    code: str
    details: Dict[str, Any]


# ============================================================================
# Project Types
# ============================================================================

ProjectType = Literal["cloud", "local", "synced"]


class ProjectSource(TypedDict, total=False):
    type: Literal["github", "gitlab", "local"]
    url: str
    branch: str
    path: str


class Project(TypedDict, total=False):
    id: str
    name: str
    description: str
    type: ProjectType
    sources: List[ProjectSource]
    userId: str
    color: Optional[str]
    defaultEnvironmentId: Optional[str]
    environmentIds: List[str]
    metadata: Dict[str, Any]
    tags: List[str]
    createdAt: str
    updatedAt: str
    deletedAt: str


class CreateProjectParams(TypedDict, total=False):
    id: str
    name: str  # required in practice
    description: str
    type: ProjectType
    sources: List[ProjectSource]
    color: Optional[str]
    environmentIds: List[str]
    defaultEnvironmentId: Optional[str]
    metadata: Dict[str, Any]
    tags: List[str]


class UpdateProjectParams(TypedDict, total=False):
    name: str
    description: str
    color: Optional[str]
    environmentIds: List[str]
    defaultEnvironmentId: Optional[str]
    metadata: Dict[str, Any]
    tags: List[str]


class ProjectStats(TypedDict, total=False):
    threadCount: int
    runCount: int
    totalTokens: int
    totalCost: float
    storageBytes: int


class ProjectSummary(TypedDict, total=False):
    environmentsCount: int
    threadsCount: int
    activeThreadsCount: int
    tasksCount: int
    openTasksCount: int
    sprintCount: int
    activeSprintCount: int
    releaseCount: int
    activeReleaseCount: int


class ProjectListParams(TypedDict, total=False):
    type: ProjectType
    q: str
    limit: int


class ProjectListResult(TypedDict):
    data: List[Project]
    hasMore: bool
    total: int


class ProjectDetailResult(TypedDict, total=False):
    project: Project
    summary: ProjectSummary
    environments: List["Environment"]
    recentThreads: List["Thread"]
    stats: ProjectStats


# ============================================================================
# Environment Types
# ============================================================================

EnvironmentStatus = Literal["stopped", "building", "running", "error"]
BuildStatus = Literal["pending", "building", "ready", "failed"]
EnvironmentComputeProfileId = Literal["lite", "standard", "power", "desktop"]


class EnvironmentVariable(TypedDict):
    key: str
    value: str


class McpServer(TypedDict, total=False):
    type: Literal["stdio", "http"]
    name: str
    command: str
    args: List[str]
    url: str
    bearerToken: str
    env: Dict[str, str]
    enabled: bool


class RuntimeConfig(TypedDict, total=False):
    python: str
    nodejs: str
    go: str
    php: str
    java: str
    ruby: str
    rust: str


class PackagesConfig(TypedDict, total=False):
    system: List[str]
    python: List[str]
    node: List[str]


class AvailableRuntimes(TypedDict):
    python: List[str]
    nodejs: List[str]
    go: List[str]
    php: List[str]
    java: List[str]
    ruby: List[str]
    rust: List[str]


class EnvironmentComputeResources(TypedDict, total=False):
    cpuCores: float
    memoryMb: int


class EnvironmentPricingMetadata(TypedDict, total=False):
    minutePrice: float


class EnvironmentMetadata(TypedDict, total=False):
    computeProfile: EnvironmentComputeProfileId
    computeResources: EnvironmentComputeResources
    pricing: EnvironmentPricingMetadata
    guiEnabled: bool
    officeAppsEnabled: bool


class Environment(TypedDict, total=False):
    id: str
    userId: str
    name: str
    description: str
    status: EnvironmentStatus
    baseImage: str
    dockerfileExtensions: str
    runtimes: RuntimeConfig
    packages: PackagesConfig
    environmentVariables: List[EnvironmentVariable]
    secrets: List[EnvironmentVariable]
    setupScripts: List[str]
    mcpServers: List[McpServer]
    documentation: List[str]
    internetAccess: bool
    buildStatus: BuildStatus
    buildHash: str
    buildError: str
    buildLogs: str
    lastBuildAt: str
    imageTag: str
    metadata: EnvironmentMetadata
    isDefault: bool
    isActive: bool
    createdAt: str
    updatedAt: str
    deletedAt: str
    projectId: str  # deprecated


Computer = Environment


class CreateEnvironmentParams(TypedDict, total=False):
    projectId: Optional[str]
    name: str  # required in practice
    description: str
    runtimes: RuntimeConfig
    packages: PackagesConfig
    dockerfileExtensions: str
    environmentVariables: List[EnvironmentVariable]
    secrets: List[EnvironmentVariable]
    setupScripts: List[str]
    mcpServers: List[McpServer]
    documentation: List[str]
    internetAccess: bool
    isDefault: bool
    computeProfile: EnvironmentComputeProfileId
    guiEnabled: bool
    officeAppsEnabled: bool
    metadata: EnvironmentMetadata


class UpdateEnvironmentParams(TypedDict, total=False):
    projectId: Optional[str]
    name: str
    description: str
    runtimes: RuntimeConfig
    packages: PackagesConfig
    dockerfileExtensions: str
    environmentVariables: List[EnvironmentVariable]
    secrets: List[EnvironmentVariable]
    setupScripts: List[str]
    mcpServers: List[McpServer]
    internetAccess: bool
    isDefault: bool
    computeProfile: EnvironmentComputeProfileId
    guiEnabled: bool
    officeAppsEnabled: bool
    metadata: EnvironmentMetadata


CreateComputerParams = CreateEnvironmentParams
UpdateComputerParams = UpdateEnvironmentParams


class ContainerStatus(TypedDict, total=False):
    status: EnvironmentStatus
    uptime: int
    memory: Dict[str, int]
    cpu: Dict[str, float]
    containerId: str
    startedAt: str
    lastUsedAt: str
    executionCount: int
    message: str


class BuildResult(TypedDict, total=False):
    success: bool
    imageTag: str
    buildHash: str
    logs: str
    error: str
    duration: int
    environmentId: str
    environmentName: str


class BuildStatusResult(TypedDict, total=False):
    buildStatus: BuildStatus
    buildHash: str
    imageTag: str
    lastBuildAt: str
    buildError: str


class BuildLogsResult(TypedDict):
    logs: str
    buildStatus: BuildStatus


class TestBuildResult(TypedDict, total=False):
    success: bool
    logs: str
    duration: int
    imageTag: str


class DockerfileResult(TypedDict, total=False):
    baseImage: str
    dockerfileExtensions: str
    effectiveDockerfile: str


class ValidateDockerfileResult(TypedDict):
    valid: bool
    warnings: List[str]
    effectiveDockerfile: str


class InstallPackagesResult(TypedDict):
    environment: Environment
    installed: List[str]


PackageType = Literal["system", "python", "node"]


class StartContainerParams(TypedDict, total=False):
    workspaceId: str
    cpus: int
    memory: str


class StartContainerResult(TypedDict):
    success: bool
    containerName: str
    containerId: str
    imageTag: str
    workspacePath: str


EnvironmentChangeKind = Literal["created", "modified", "deleted"]
EnvironmentChangeOperation = Literal["created", "uploaded", "modified", "deleted"]
EnvironmentChangeSourceKind = Literal["thread", "manual"]


class EnvironmentSnapshot(TypedDict, total=False):
    id: str
    environmentId: str
    sourceThreadId: Optional[str]
    sourceStepId: Optional[str]
    parentSnapshotId: Optional[str]
    ledgerCommitSha: str
    changedPaths: List[str]
    additions: int
    deletions: int
    metadata: Dict[str, Any]
    createdAt: str


class EnvironmentChangeFileRecord(TypedDict, total=False):
    path: str
    name: str
    changeKind: EnvironmentChangeKind
    operation: EnvironmentChangeOperation
    entryType: Literal["file", "directory"]
    previousPath: Optional[str]
    additions: int
    deletions: int
    diff: Optional[str]
    fileContent: Optional[str]


class EnvironmentChangeEntry(TypedDict, total=False):
    id: str
    snapshotId: str
    environmentId: str
    createdAt: str
    title: str
    routeSource: Optional[str]
    sourceKind: EnvironmentChangeSourceKind
    sourceThreadId: Optional[str]
    sourceStepId: Optional[str]
    threadTitle: Optional[str]
    stepTitle: Optional[str]
    projectId: Optional[str]
    projectName: Optional[str]
    agentId: Optional[str]
    agentName: Optional[str]
    additions: int
    deletions: int
    files: List[EnvironmentChangeFileRecord]


class EnvironmentChangeListResponse(TypedDict):
    object: Literal["list"]
    limit: int
    offset: int
    total: int
    hasMore: bool
    data: List[EnvironmentChangeEntry]


class SnapshotFileEntry(TypedDict, total=False):
    path: str
    name: str
    type: Literal["file", "directory"]
    size: Optional[int]


class EnvironmentSnapshotFilesResponse(TypedDict, total=False):
    object: Literal["list"]
    environmentId: str
    snapshotId: str
    prefix: Optional[str]
    data: List[SnapshotFileEntry]


class EnvironmentSnapshotDiffResponse(TypedDict, total=False):
    environmentId: str
    snapshotId: str
    parentSnapshotId: Optional[str]
    fromCommitSha: Optional[str]
    toCommitSha: str
    path: Optional[str]
    diff: str
    changedPaths: List[str]
    additions: int
    deletions: int


class EnvironmentSnapshotFileResponse(TypedDict, total=False):
    path: str
    snapshotId: Optional[str]
    content: str


class EnvironmentForkFromSnapshotResponse(TypedDict, total=False):
    environment: Environment
    snapshot: Optional[EnvironmentSnapshot]
    sourceSnapshotId: str


# ============================================================================
# Thread Types
# ============================================================================

ThreadStatus = Literal[
    "active", "running", "permission_asked", "completed", "failed",
    "archived", "cancelled", "deleted",
]


class ThreadMessage(TypedDict, total=False):
    role: Literal["user", "assistant", "system"]
    content: str
    timestamp: str


class Thread(TypedDict, total=False):
    id: str
    projectId: str
    environmentId: str
    agentId: str
    title: str
    status: ThreadStatus
    messages: List[ThreadMessage]
    messageCount: int
    totalTokens: int
    totalCost: float
    createdAt: str
    updatedAt: str
    deletedAt: str


class CreateThreadParams(TypedDict, total=False):
    environmentId: str  # required
    agentId: str
    title: str


class UpdateThreadParams(TypedDict, total=False):
    title: str
    status: ThreadStatus


class ListThreadsParams(TypedDict, total=False):
    limit: int
    offset: int
    environmentId: str
    status: ThreadStatus


class CopyThreadParams(TypedDict, total=False):
    title: str


class SearchThreadsParams(TypedDict, total=False):
    query: str  # required
    environmentId: str
    status: Union[ThreadStatus, Literal["all"]]
    limit: int
    offset: int
    includeMessages: bool


class SearchThreadResult(TypedDict, total=False):
    thread: Thread
    score: float
    highlights: List[str]
    matchingMessages: List[ThreadMessage]


class SearchThreadsResponse(TypedDict):
    results: List[SearchThreadResult]
    total: int
    hasMore: bool
    searchMetadata: Dict[str, Any]


class ThreadLogEntry(TypedDict, total=False):
    role: Literal["user", "assistant", "execution_log"]
    content: str
    timestamp: str
    relativeTime: str
    logType: str
    metadata: Optional[Dict[str, Any]]


class ResearchSession(TypedDict, total=False):
    id: str
    threadId: str
    status: str
    progress: float
    query: str
    results: List[Any]
    createdAt: str
    updatedAt: str


ThreadFeedbackRating = Literal["up", "down"]
ThreadFeedbackReportType = Literal["general", "bug", "child_safety", "response"]


class ThreadFeedbackSummary(TypedDict):
    threadId: str
    upCount: int
    downCount: int
    userRating: Optional[ThreadFeedbackRating]
    reportCount: int


class ThreadFeedbackReportCreate(TypedDict, total=False):
    reportType: ThreadFeedbackReportType
    message: str
    metadata: Optional[Dict[str, Any]]


class ThreadFeedbackReport(TypedDict, total=False):
    id: str
    threadId: str
    userId: str
    reportType: ThreadFeedbackReportType
    message: str
    metadata: Optional[Dict[str, Any]]
    createdAt: str


class ThreadPermissionRequest(TypedDict, total=False):
    requestId: str
    threadId: str
    userId: str
    toolName: str
    input: str
    currentMode: str
    requiredMode: str
    reason: Optional[str]
    createdAt: str


class ThreadPermissionDecisionParams(TypedDict, total=False):
    decision: Literal["allow", "deny"]
    reason: Optional[str]


class ThreadPermissionDecisionResponse(TypedDict, total=False):
    ok: bool
    requestId: str
    decision: Literal["allow", "deny"]
    active: bool
    message: Optional[str]


# ============================================================================
# Task Types
# ============================================================================

TaskStatus = Literal["backlog", "todo", "in_progress", "blocked", "in_review", "done"]
TaskPriority = Literal["low", "medium", "high", "urgent"]
TaskType = Literal["task", "subtask"]
TaskCommentAuthorType = Literal["user", "agent", "system"]
TaskSprintStatus = Literal["planned", "active", "completed"]
TaskReleaseStatus = Literal["planned", "active", "completed"]


class Task(TypedDict, total=False):
    object: Literal["task"]
    id: str
    userId: str
    projectId: Optional[str]
    releaseId: Optional[str]
    sprintId: Optional[str]
    title: str
    description: str
    status: TaskStatus
    priority: TaskPriority
    type: TaskType
    parentTaskId: Optional[str]
    assigneeAgentId: Optional[str]
    dependencyIds: List[str]
    linkedThreadIds: List[str]
    lastStartedThreadId: Optional[str]
    scheduledStartAt: Optional[str]
    scheduledEndAt: Optional[str]
    dueAt: Optional[str]
    completedAt: Optional[str]
    sortOrder: float
    reviewRequired: bool
    reviewerActorId: Optional[str]
    reviewerActorKind: Optional[str]
    reviewerName: Optional[str]
    metadata: Optional[Dict[str, Any]]
    createdAt: str
    updatedAt: str


class TaskListParams(TypedDict, total=False):
    limit: int
    offset: int
    projectId: Optional[str]
    releaseId: Optional[str]
    sprintId: Optional[str]
    status: TaskStatus
    assigneeAgentId: str
    q: str


class CreateTaskParams(TypedDict, total=False):
    title: str
    description: str
    projectId: Optional[str]
    releaseId: Optional[str]
    status: TaskStatus
    priority: TaskPriority
    type: TaskType
    taskType: TaskType
    parentTaskId: Optional[str]
    sprintId: Optional[str]
    assigneeAgentId: Optional[str]
    dependencyIds: List[str]
    linkedThreadIds: List[str]
    lastStartedThreadId: Optional[str]
    scheduledStartAt: Optional[str]
    scheduledEndAt: Optional[str]
    dueAt: Optional[str]
    completedAt: Optional[str]
    sortOrder: float
    metadata: Optional[Dict[str, Any]]


class UpdateTaskParams(CreateTaskParams, total=False):
    pass


class TaskListResult(TypedDict):
    data: List[Task]
    hasMore: bool
    total: int


class TaskDetails(TypedDict, total=False):
    project: Optional[Project]
    release: Optional["TaskRelease"]
    sprint: Optional["TaskSprint"]
    assignee: Optional["CloudAgent"]
    dependencies: List[Task]
    dependents: List[Task]
    subtasks: List[Task]
    subtaskIds: List[str]
    parentTask: Optional[Task]
    parentTaskId: Optional[str]
    taskType: TaskType
    review: Optional[Dict[str, Any]]
    linkedThreads: List[Thread]
    lastStartedThread: Optional[Thread]
    blockedByDependencyIds: List[str]
    readyToStart: bool


class TaskDetailResult(TypedDict, total=False):
    task: Task
    details: TaskDetails
    comments: List["TaskComment"]


class TaskComment(TypedDict, total=False):
    object: Literal["task.comment"]
    id: str
    userId: str
    projectId: Optional[str]
    taskId: str
    task: Task
    body: str
    authorType: TaskCommentAuthorType
    authorAgentId: Optional[str]
    authorName: Optional[str]
    sourceThreadId: Optional[str]
    threadId: Optional[str]
    metadata: Optional[Dict[str, Any]]
    createdAt: str
    updatedAt: str


class TaskCommentCreateParams(TypedDict, total=False):
    body: str
    content: str
    authorType: TaskCommentAuthorType
    authorAgentId: Optional[str]
    authorName: Optional[str]
    sourceThreadId: Optional[str]
    threadId: Optional[str]
    metadata: Optional[Dict[str, Any]]


class TaskCommentListParams(TypedDict, total=False):
    authorType: TaskCommentAuthorType
    authorAgentId: str
    limit: int
    offset: int


class TaskCommentListResult(TypedDict):
    data: List[TaskComment]
    hasMore: bool
    total: int


class TaskSprint(TypedDict, total=False):
    id: str
    userId: str
    projectId: Optional[str]
    name: str
    goal: str
    status: TaskSprintStatus
    startAt: Optional[str]
    endAt: Optional[str]
    sortOrder: float
    metadata: Optional[Dict[str, Any]]
    createdAt: str
    updatedAt: str


class TaskSprintCreateParams(TypedDict, total=False):
    projectId: Optional[str]
    name: str
    goal: str
    status: TaskSprintStatus
    startAt: Optional[str]
    endAt: Optional[str]
    sortOrder: float
    metadata: Optional[Dict[str, Any]]


class TaskSprintUpdateParams(TaskSprintCreateParams, total=False):
    pass


class TaskSprintListParams(TypedDict, total=False):
    projectId: Optional[str]
    status: TaskSprintStatus
    q: str
    limit: int
    offset: int


class TaskSprintListResult(TypedDict):
    data: List[TaskSprint]
    hasMore: bool
    total: int


class TaskSprintDetailResult(TypedDict, total=False):
    sprint: TaskSprint
    tasks: List[Task]


class TaskRelease(TypedDict, total=False):
    object: Literal["task.release"]
    id: str
    userId: str
    projectId: Optional[str]
    name: str
    description: str
    startAt: Optional[str]
    endAt: Optional[str]
    sortOrder: float
    status: TaskReleaseStatus
    metadata: Optional[Dict[str, Any]]
    taskCount: int
    openTaskCount: int
    taskIds: List[str]
    createdAt: str
    updatedAt: str


class TaskReleaseCreateParams(TypedDict, total=False):
    projectId: str
    name: str
    description: str
    startAt: Optional[str]
    endAt: Optional[str]
    sortOrder: float
    metadata: Optional[Dict[str, Any]]


class TaskReleaseUpdateParams(TaskReleaseCreateParams, total=False):
    pass


class TaskReleaseListParams(TypedDict, total=False):
    projectId: str
    q: str
    limit: int
    offset: int


class TaskReleaseListResult(TypedDict):
    data: List[TaskRelease]
    hasMore: bool
    total: int


class TaskReleaseDetailResult(TypedDict, total=False):
    release: TaskRelease
    tasks: List[Task]


class TaskWorkspaceParams(TypedDict, total=False):
    projectId: Optional[str]
    q: str
    rangeStart: str
    rangeEnd: str


class TaskWorkspaceResult(TypedDict):
    workspace: Dict[str, Any]


class TaskStartThreadParams(TypedDict, total=False):
    environmentId: str
    agentId: str
    moveToInProgress: bool
    metadata: Optional[Dict[str, Any]]


class TaskStartThreadResult(TypedDict, total=False):
    thread: Thread
    task: Task
    subtasks: List[Task]


class TaskRunThreadParams(TaskStartThreadParams, total=False):
    message: str
    content: str
    task: str


class TaskRunThreadResult(TaskStartThreadResult, total=False):
    execution: Dict[str, Any]


# ============================================================================
# Agent Config & Send Message
# ============================================================================

BuiltinAgentModel = Literal[
    "claude-opus-4-7",
    "claude-opus-4-6",
    "claude-sonnet-4-5",
    "claude-haiku-4-5",
    "gpt-5.5-pro",
    "gpt-5.5",
    "gpt-5.4",
    "gpt-5.4-mini",
    "gpt-5.4-nano",
    "gemini-3-flash",
    "gemini-3-1-flash",
    "gemini-3-1-pro",
    "deepseek-v4-pro",
    "deepseek-v4-flash",
    "kimi-k2.6",
]
AgentModel = str
ReasoningEffort = Literal["minimal", "low", "medium", "high"]
DeepResearchModel = str


class AgentConfig(TypedDict, total=False):
    model: AgentModel
    instructions: str
    reasoningEffort: ReasoningEffort


class SendMessageParams(TypedDict, total=False):
    content: str  # required
    mcpServers: List[McpServer]
    envVars: Dict[str, str]
    secrets: List[EnvironmentVariable]
    setupScripts: List[str]
    agentConfig: AgentConfig
    internetAccess: bool
    attachments: List[Any]
    runId: str


# ============================================================================
# SSE Event Types
# ============================================================================

class StreamEvent(TypedDict, total=False):
    type: str
    timestamp: str


class ResponseStartedEvent(TypedDict, total=False):
    type: Literal["response.started"]
    timestamp: str


class ResponseItemCompletedEvent(TypedDict, total=False):
    type: Literal["response.item.completed"]
    timestamp: str
    item: Dict[str, Any]


class ResponseCompletedEvent(TypedDict, total=False):
    type: Literal["response.completed"]
    timestamp: str
    response: Dict[str, Any]


class StreamCompletedEvent(TypedDict, total=False):
    type: Literal["stream.completed"]
    timestamp: str
    run: Dict[str, Any]


class StreamErrorEvent(TypedDict, total=False):
    type: Literal["stream.error"]
    timestamp: str
    error: str
    message: str


MessageStreamEvent = Union[
    ResponseStartedEvent,
    ResponseItemCompletedEvent,
    ResponseCompletedEvent,
    StreamCompletedEvent,
    StreamErrorEvent,
    Dict[str, Any],  # fallback for unknown events
]


# ============================================================================
# Run Types
# ============================================================================

RunStatus = Literal["pending", "running", "success", "failed", "cancelled"]


class TokenUsage(TypedDict, total=False):
    inputTokens: int
    outputTokens: int
    cachedTokens: int


class Run(TypedDict, total=False):
    id: str
    projectId: str
    threadId: str
    environmentId: str
    agentId: str
    agentName: str
    name: str
    task: str
    prompt: str
    status: RunStatus
    duration: int
    cost: float
    tokenUsage: TokenUsage
    metadata: Dict[str, Any]
    createdAt: str
    updatedAt: str
    completedAt: str
    deletedAt: str


class CreateRunParams(TypedDict, total=False):
    agentId: str
    agentName: str  # required
    name: str  # required
    task: str  # required
    prompt: str
    title: str
    workspaceName: str
    workspaceId: str
    contextId: str
    environmentId: str
    environmentName: str
    attachments: List[Any]
    metadata: Dict[str, Any]
    threadId: str


class UpdateRunParams(TypedDict, total=False):
    name: str
    status: RunStatus
    duration: int
    cost: float
    logs: List[Any]
    metadata: Dict[str, Any]
    tokenUsage: TokenUsage
    title: str


class ListRunsParams(TypedDict, total=False):
    limit: int
    offset: int
    threadId: str
    status: RunStatus
    since: str


class RunLogEntry(TypedDict, total=False):
    timestamp: str
    level: Literal["info", "warning", "error", "debug"]
    message: str
    metadata: Dict[str, Any]


class RunDiff(TypedDict, total=False):
    path: str
    type: Literal["created", "modified", "deleted", "renamed"]
    diff: str
    additions: int
    deletions: int


# ============================================================================
# Agent Types
# ============================================================================

PermissionAccessLevel = Literal["full_access", "ask_for_permission", "read_only", "no_access"]
PermissionResourceType = Literal["agents", "skills", "servers", "computers", "files", "directories", "projects"]
PermissionSetSubjectType = Literal["agent", "human_user", "team"]


class PermissionRule(TypedDict, total=False):
    id: str
    targetId: str
    path: str
    access: PermissionAccessLevel
    note: str


class PermissionResourcePolicy(TypedDict, total=False):
    defaultAccess: PermissionAccessLevel
    rules: List[PermissionRule]


class PermissionSet(TypedDict, total=False):
    version: Literal[1]
    subjectType: PermissionSetSubjectType
    defaultAccess: PermissionAccessLevel
    resources: Dict[PermissionResourceType, PermissionResourcePolicy]


class AgentBinary(TypedDict, total=False):
    path: str
    args: List[str]


class CloudAgent(TypedDict, total=False):
    id: str
    projectId: str
    name: str
    description: str
    model: AgentModel
    instructions: str
    binary: AgentBinary
    reasoningEffort: ReasoningEffort
    enabledSkills: List[str]
    deepResearchModel: DeepResearchModel
    permissionSet: PermissionSet
    metadata: Dict[str, Any]
    createdAt: str
    updatedAt: str
    deletedAt: str


class CreateAgentParams(TypedDict, total=False):
    name: str  # required
    description: str
    model: AgentModel  # required
    instructions: str
    binary: AgentBinary
    reasoningEffort: ReasoningEffort
    enabledSkills: List[str]
    deepResearchModel: DeepResearchModel
    permissionSet: PermissionSet
    metadata: Dict[str, Any]


class UpdateAgentParams(TypedDict, total=False):
    name: str
    description: str
    model: AgentModel
    instructions: str
    reasoningEffort: ReasoningEffort
    enabledSkills: List[str]
    deepResearchModel: DeepResearchModel
    permissionSet: Optional[PermissionSet]
    metadata: Dict[str, Any]


# ============================================================================
# Budget & Billing Types
# ============================================================================

class BudgetStatus(TypedDict):
    balance: float
    spent: float
    limit: float
    remaining: float


class CanExecuteResult(TypedDict, total=False):
    canExecute: bool
    reason: str


class IncreaseBudgetParams(TypedDict, total=False):
    amount: float  # required
    description: str
    stripePaymentIntentId: str
    stripeChargeId: str
    paymentMethod: str


class IncreaseBudgetResult(TypedDict):
    success: bool
    budget: Dict[str, float]


class BillingRecord(TypedDict, total=False):
    id: str
    type: Literal["execution", "credit", "mcp_usage", "adjustment"]
    amount: float
    runId: str
    description: str
    createdAt: str


class ListBillingRecordsParams(TypedDict, total=False):
    limit: int
    offset: int
    since: str
    until: str
    type: Literal["execution", "credit", "mcp_usage", "adjustment"]


class BillingAccount(TypedDict, total=False):
    apiKeyId: str
    type: Literal["standard", "internal"]
    status: Literal["active", "suspended"]
    monthlyBudget: float
    currentBalance: float
    billingEmail: str
    createdAt: str


class UsageStats(TypedDict, total=False):
    period: Literal["day", "week", "month", "year"]
    startDate: str
    endDate: str
    totalCost: float
    totalTokens: int
    totalRuns: int
    breakdown: Dict[str, Dict[str, Any]]


class UsageStatsParams(TypedDict, total=False):
    period: Literal["day", "week", "month", "year"]
    breakdown: Literal["project", "model", "agent"]


# ============================================================================
# File Types
# ============================================================================

class FileEntry(TypedDict, total=False):
    name: str
    path: str
    type: Literal["file", "directory"]
    size: int
    mimeType: str
    modifiedAt: str


class ListFilesParams(TypedDict, total=False):
    path: str
    environmentId: str
    recursive: bool


class UploadFileParams(TypedDict, total=False):
    path: str  # required
    content: Any  # str or bytes; required
    contentType: str
    environmentId: str


class CreateDirectoryParams(TypedDict, total=False):
    path: str  # required
    environmentId: str


# ============================================================================
# Notification Types
# ============================================================================

class InAppNotification(TypedDict, total=False):
    id: str
    html: str
    createdAt: str
    createdBy: Optional[str]
    expiresAt: Optional[str]
    metadata: Dict[str, Any]


class PushTokenRegistration(TypedDict, total=False):
    token: str
    platform: str
    bundleId: str


class PushTokenRegistrationResponse(TypedDict):
    success: bool
    tokenId: str


class PushTokenDeleteResponse(TypedDict):
    success: bool


class PushTokenDescriptor(TypedDict):
    id: str
    platform: str


# ============================================================================
# Git Types
# ============================================================================

class GitDiffFile(TypedDict, total=False):
    path: str
    additions: int
    deletions: int
    changes: str


class GitDiffResult(TypedDict, total=False):
    diffs: List[GitDiffFile]
    stats: Dict[str, Any]


class GitCommitParams(TypedDict, total=False):
    message: str  # required
    author: Dict[str, str]
    files: List[str]


class GitCommitResult(TypedDict):
    success: bool
    commit: Dict[str, Any]


class GitPushParams(TypedDict, total=False):
    remote: str
    branch: str
    force: bool


class GitPushResult(TypedDict):
    success: bool
    push: Dict[str, Any]


# ============================================================================
# Schedule Types
# ============================================================================

ScheduleType = Literal["one-time", "recurring"]


class Schedule(TypedDict, total=False):
    id: str
    projectId: str
    name: str
    description: str
    agentId: str
    agentName: str
    task: str
    workspaceId: str
    workspaceName: str
    contextId: str
    contextName: str
    environmentId: str
    environmentName: str
    scheduleType: ScheduleType
    cronExpression: str
    scheduledTime: str
    timezone: str
    enabled: bool
    lastRunAt: str
    nextRunAt: str
    metadata: Dict[str, Any]
    createdAt: str
    updatedAt: str
    deletedAt: str


class CreateScheduleParams(TypedDict, total=False):
    name: str  # required
    description: str
    agentId: str  # required
    agentName: str  # required
    task: str  # required
    workspaceId: str
    workspaceName: str
    contextId: str
    contextName: str
    environmentId: str
    environmentName: str
    scheduleType: ScheduleType  # required
    cronExpression: str
    scheduledTime: str
    timezone: str
    enabled: bool
    metadata: Dict[str, Any]


class UpdateScheduleParams(TypedDict, total=False):
    name: str
    description: str
    task: str
    cronExpression: str
    scheduledTime: str
    timezone: str
    enabled: bool
    metadata: Dict[str, Any]


# ============================================================================
# Trigger Types
# ============================================================================

TriggerSource = Literal["github", "gitlab", "slack", "email", "webhook", "cron", "custom"]


class TriggerAction(TypedDict, total=False):
    type: Literal["send_message", "comment_pull_request", "comment_merge_request"]
    prompt: str
    message: str
    template: str


class Trigger(TypedDict, total=False):
    id: str
    name: str
    environmentId: str
    agentId: str
    source: TriggerSource
    event: str
    filters: Dict[str, Any]
    action: TriggerAction
    enabled: bool
    lastTriggeredAt: int
    createdAt: int
    updatedAt: int


class CreateTriggerParams(TypedDict, total=False):
    name: str  # required
    environmentId: str  # required
    agentId: str
    source: TriggerSource  # required
    event: str  # required
    filters: Dict[str, Any]
    action: TriggerAction  # required
    enabled: bool


class UpdateTriggerParams(TypedDict, total=False):
    name: str
    agentId: str
    event: str
    filters: Dict[str, Any]
    action: TriggerAction
    enabled: bool


class TriggerExecution(TypedDict, total=False):
    id: str
    triggerId: str
    threadId: str
    event: Dict[str, Any]
    status: Literal["pending", "running", "completed", "failed"]
    createdAt: int


# ============================================================================
# Orchestration Types
# ============================================================================

OrchestrationStrategy = Literal["parallel", "sequential", "conditional", "map_reduce"]


class OrchestrationStep(TypedDict, total=False):
    id: str
    agentId: str
    name: str
    instructions: str
    inputs: Dict[str, Any]
    dependsOn: List[str]
    condition: str


class Orchestration(TypedDict, total=False):
    id: str
    name: str
    environmentId: str
    strategy: OrchestrationStrategy
    coordinatorAgentId: str
    steps: List[OrchestrationStep]
    status: Literal["draft", "active", "archived"]
    createdAt: int
    updatedAt: int


class CreateOrchestrationParams(TypedDict, total=False):
    name: str  # required
    environmentId: str  # required
    strategy: OrchestrationStrategy  # required
    coordinatorAgentId: str
    steps: List[Dict[str, Any]]  # required; steps without 'id'


class UpdateOrchestrationParams(TypedDict, total=False):
    name: str
    strategy: OrchestrationStrategy
    coordinatorAgentId: str
    steps: List[Dict[str, Any]]


class OrchestrationStepResult(TypedDict, total=False):
    stepId: str
    agentId: str
    status: Literal["pending", "running", "completed", "failed", "skipped"]
    output: str
    error: str
    durationMs: int


class OrchestrationRun(TypedDict, total=False):
    id: str
    orchestrationId: str
    threadId: str
    status: Literal["pending", "running", "completed", "failed"]
    stepResults: List[OrchestrationStepResult]
    createdAt: int
    completedAt: int


# ============================================================================
# Health Types
# ============================================================================

class HealthCheck(TypedDict, total=False):
    status: Literal["healthy", "unhealthy"]
    timestamp: str
    uptime: int
    checks: Dict[str, Any]
    metrics: Dict[str, Any]


class Metrics(TypedDict, total=False):
    totalExecutions: int
    successfulExecutions: int
    failedExecutions: int
    averageDuration: int
    totalTokensUsed: int
    totalCost: float
