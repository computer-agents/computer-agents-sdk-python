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


class ProjectOwner(TypedDict, total=False):
    userId: str
    name: str
    email: str
    avatarUrl: str


class Project(TypedDict, total=False):
    object: Literal["project", "project.overview"]
    isOverviewRecord: bool
    id: str
    name: str
    description: str
    type: ProjectType
    primarySource: str
    sources: List[ProjectSource]
    userId: str
    ownerUserId: str
    ownerName: str
    ownerEmail: str
    ownerAvatarUrl: str
    owner: ProjectOwner
    canTransferOwnership: bool
    organizationId: Optional[str]
    createdByUserId: Optional[str]
    createdByName: Optional[str]
    createdByEmail: Optional[str]
    createdByAvatarUrl: Optional[str]
    createdBy: Optional[ProjectOwner]
    color: Optional[str]
    defaultEnvironmentId: Optional[str]
    environmentIds: List[str]
    permissionSet: PermissionSet
    metadata: Optional[Dict[str, Any]]
    sharedWithMe: bool
    isShared: bool
    teamShared: bool
    teamShareId: Optional[str]
    teamId: Optional[str]
    teamName: Optional[str]
    teamAccessLevel: Optional[Literal["use", "edit", "manage"]]
    teamShareSource: Optional[Literal["resource_share", "project_settings"]]
    summary: ProjectSummary
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
    permissionSet: PermissionSet
    missionControl: Dict[str, Any]
    tags: List[str]


class UpdateProjectParams(TypedDict, total=False):
    name: str
    description: str
    color: Optional[str]
    environmentIds: List[str]
    defaultEnvironmentId: Optional[str]
    cloneProjectDirectory: bool
    metadata: Dict[str, Any]
    permissionSet: PermissionSet
    missionControl: Dict[str, Any]
    tags: List[str]


class ProjectStats(TypedDict, total=False):
    threadCount: int
    runCount: int
    totalTokens: int
    totalCost: float
    totalCostUsd: float
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
    view: Literal["overview"]


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


class ProjectMissionControlFocus(TypedDict, total=False):
    issues: bool
    strategy: bool
    milestones: bool
    knowledge: bool


class StartProjectMissionControlParams(TypedDict, total=False):
    agentId: str  # required in practice
    focus: ProjectMissionControlFocus
    environmentId: Optional[str]
    instructions: str


class ProjectMissionControlRunResult(TypedDict):
    thread: "Thread"
    metronome: Dict[str, Any]
    run: Dict[str, Any]
    output: Any


class ProjectMentionReference(TypedDict, total=False):
    kind: Literal["human", "agent"]
    id: str
    label: str


class ProjectMentionCandidate(TypedDict):
    kind: Literal["human", "agent"]
    id: str
    label: str
    description: str
    avatarUrl: Optional[str]


class CreateProjectActivityCommentParams(TypedDict, total=False):
    body: str  # required in practice
    idempotencyKey: str
    mentions: List[ProjectMentionReference]


class ProjectActivityCommentResult(TypedDict, total=False):
    comment: "ProjectUpdateComment"
    mentionDispatches: List[Dict[str, Any]]
    project: Project


ProjectWorkRelationType = Literal[
    "blocks",
    "parent_of",
    "duplicates",
    "relates_to",
]


class ProjectWorkRelation(TypedDict):
    id: str
    userId: str
    organizationId: Optional[str]
    createdByUserId: Optional[str]
    projectId: str
    sourceTaskId: str
    targetTaskId: str
    relationType: ProjectWorkRelationType
    metadata: Optional[Dict[str, Any]]
    createdAt: str
    updatedAt: str


class CreateProjectWorkRelationParams(TypedDict, total=False):
    sourceTaskId: str
    targetTaskId: str
    relationType: ProjectWorkRelationType
    metadata: Optional[Dict[str, Any]]


TaskAgentSessionState = Literal[
    "queued",
    "active",
    "awaiting_input",
    "completed",
    "failed",
    "canceled",
    "stale",
]
TaskAgentSessionTriggerKind = Literal[
    "manual",
    "automation",
    "schedule",
    "api",
    "retry",
]


class TaskAgentSession(TypedDict):
    id: str
    userId: str
    organizationId: Optional[str]
    createdByUserId: Optional[str]
    projectId: Optional[str]
    taskId: str
    threadId: str
    agentId: Optional[str]
    environmentId: Optional[str]
    state: TaskAgentSessionState
    triggerKind: TaskAgentSessionTriggerKind
    attemptNumber: int
    idempotencyKey: Optional[str]
    executionConfig: Optional[Dict[str, Any]]
    limits: Optional[Dict[str, Any]]
    inputTokens: int
    outputTokens: int
    costUsd: Optional[float]
    errorCode: Optional[str]
    errorMessage: Optional[str]
    startedAt: Optional[str]
    completedAt: Optional[str]
    metadata: Optional[Dict[str, Any]]
    createdAt: str
    updatedAt: str


class TaskAgentSessionListResult(TypedDict):
    data: List[TaskAgentSession]
    hasMore: bool


class TaskAgentSessionMetrics(TypedDict):
    generatedAt: str
    windowStartedAt: Optional[str]
    totalAttempts: int
    stateCounts: Dict[TaskAgentSessionState, int]
    terminalAttempts: int
    successfulAttempts: int
    failedAttempts: int
    successRate: float
    failureRate: float
    stalledAttempts: int
    totalInputTokens: int
    totalOutputTokens: int
    totalTokens: int
    totalCostUsd: float
    averageDurationMs: Optional[int]
    p95DurationMs: Optional[int]


class ProjectAgentSessionSummary(TypedDict):
    projectId: str
    window: Literal["24h", "7d", "30d", "all"]
    metrics: TaskAgentSessionMetrics


class ProjectWorkGraph(TypedDict):
    projectId: str
    tasks: List["Task"]
    relations: List[ProjectWorkRelation]
    agentSessions: List[TaskAgentSession]


ProjectDeliveryMode = Literal["assisted", "autonomous"]
ProjectDeliveryStageId = Literal[
    "build",
    "test",
    "evaluate",
    "optimize",
    "re_evaluate",
    "acceptance_evaluate",
    "assure",
    "release",
    "deliver",
]
ProjectDeliveryRepairableStage = Literal[
    "test",
    "evaluate",
    "acceptance_evaluate",
]


class ProjectDeliveryValidationAsset(TypedDict, total=False):
    id: str
    name: str
    uri: str
    kind: Literal[
        "validation_set",
        "training_set",
        "specification",
        "source_document",
        "other",
    ]
    sha256: Optional[str]


class ProjectDeliveryEvaluationCase(TypedDict, total=False):
    id: str
    input: str
    expectedOutput: str
    evaluationGuidance: str
    optimizationRole: Literal["train", "validation", "holdout"]
    metadata: Dict[str, Any]


class EvaluationDatasetGovernance(TypedDict):
    schemaVersion: Literal[
        "computer_agents_evaluation_dataset_governance_v1"
    ]
    maturity: Literal[
        "diagnostic",
        "development",
        "validation",
        "locked_test",
        "external_test",
    ]
    adjudicationStatus: Literal["pending", "in_progress", "adjudicated"]
    allowedPurposes: List[Literal[
        "diagnostic",
        "development",
        "optimization",
        "release",
        "external_validation",
    ]]
    annotationGuidelineVersion: Optional[str]
    adjudicationRecordSha256: Optional[str]
    lockedAt: Optional[str]


class ProjectDeliveryRepairPolicy(TypedDict, total=False):
    enabled: bool
    maximumAttempts: int
    repairableStages: List[ProjectDeliveryRepairableStage]
    requireChangedResourceRevision: Literal[True]


class ProjectDeliveryContract(TypedDict, total=False):
    schemaVersion: Literal[
        "computer_agents_project_delivery_contract_v1",
        "computer_agents_project_delivery_contract_v2",
        "computer_agents_project_delivery_contract_v4",
    ]
    mode: ProjectDeliveryMode
    goal: str
    validationAssets: List[ProjectDeliveryValidationAsset]
    agents: Dict[str, Any]
    services: Dict[str, Any]
    acceptance: Dict[str, Any]
    budget: Dict[str, Any]
    repairPolicy: ProjectDeliveryRepairPolicy


class ProjectDeliveryGraphNode(TypedDict, total=False):
    id: ProjectDeliveryStageId
    title: str
    state: Literal["planned", "blocked", "skipped"]
    dependsOn: List[ProjectDeliveryStageId]
    resourceTypes: List[str]
    taskId: str
    resourceIds: List[str]


class ProjectDeliveryGraph(TypedDict, total=False):
    schemaVersion: Literal[
        "computer_agents_project_delivery_graph_v1",
        "computer_agents_project_delivery_graph_v2",
    ]
    contractFingerprint: str
    nodes: List[ProjectDeliveryGraphNode]
    edges: List[Dict[str, ProjectDeliveryStageId]]


class ProjectDeliveryEvaluationPreview(TypedDict):
    source: Literal["inline", "existing_evaluation_version"]
    caseCount: int
    targetKind: Literal["agent", "function", "metronome", "service_topology"]
    evaluatorType: Literal["exact", "agent", "deterministic"]
    passThreshold: float
    runPurpose: Literal["development", "optimization", "release"]
    datasetMaturity: Literal[
        "diagnostic",
        "development",
        "validation",
        "locked_test",
        "external_test",
    ]
    adjudicationStatus: Literal["pending", "in_progress", "adjudicated"]
    allowedPurposes: List[str]


class ProjectDeliveryPreview(TypedDict, total=False):
    schemaVersion: Literal["computer_agents_project_delivery_preview_v1"]
    contractSchemaVersion: Literal["computer_agents_project_delivery_contract_v4"]
    contractFingerprint: str
    contract: ProjectDeliveryContract
    graph: ProjectDeliveryGraph
    intent: Dict[str, Any]
    validationAssets: Dict[str, Any]
    topology: Dict[str, Any]
    stages: Dict[str, List[ProjectDeliveryStageId]]
    services: Dict[str, Any]
    acceptance: Dict[str, Any]
    budget: Dict[str, Any]
    repairPolicy: Dict[str, Any]


class ProjectDeliveryPlanEvent(TypedDict, total=False):
    id: str
    type: str
    actorUserId: Optional[str]
    payload: Dict[str, Any]
    createdAt: str


class ProjectDeliveryPlan(TypedDict, total=False):
    id: str
    projectId: str
    userId: str
    organizationId: Optional[str]
    createdByUserId: Optional[str]
    schemaVersion: Literal["computer_agents_project_delivery_contract_v4"]
    contract: ProjectDeliveryContract
    contractFingerprint: str
    graph: ProjectDeliveryGraph
    bindings: Dict[str, Any]
    status: Literal["draft", "provisioning", "ready", "failed", "archived"]
    revision: int
    idempotencyKey: Optional[str]
    error: Optional[str]
    provisionedAt: Optional[str]
    createdAt: str
    updatedAt: str
    events: List[ProjectDeliveryPlanEvent]


ProjectDeliveryExecutionStatus = Literal[
    "queued",
    "running",
    "blocked",
    "failed",
    "passed",
    "cancelled",
]
ProjectDeliveryStageStatus = Literal[
    "pending",
    "running",
    "blocked",
    "passed",
    "failed",
    "skipped",
]


class ProjectDeliveryStageState(TypedDict, total=False):
    id: ProjectDeliveryStageId
    status: ProjectDeliveryStageStatus
    retryCount: int
    taskId: str
    resourceIds: List[str]
    evidence: Dict[str, Any]
    error: Optional[str]
    startedAt: Optional[str]
    completedAt: Optional[str]


class ProjectDeliveryRepairEpisode(TypedDict, total=False):
    schemaVersion: Literal[
        "computer_agents_project_delivery_repair_episode_v1"
    ]
    id: str
    sourceStage: ProjectDeliveryRepairableStage
    repairAttempt: int
    maximumAttempts: int
    repairTaskId: str
    testPlanId: str
    testPlanVersionId: str
    failedRunId: str
    failedRunStatus: str
    failedCommitSha: str
    failureMessage: str
    evidenceFingerprint: str
    resultSetFingerprint: str
    artifactSetFingerprint: str
    reportFingerprint: Optional[str]
    evaluationId: Optional[str]
    evaluationVersionId: Optional[str]
    failedTargetType: Optional[str]
    failedTargetId: Optional[str]
    failedTargetVersionId: Optional[str]
    failedTargetFingerprint: Optional[str]
    averageScore: Optional[float]
    passRate: Optional[float]
    minimumAverageScore: Optional[float]
    minimumPassRate: Optional[float]
    diagnosticFingerprint: str
    failedCases: List[Dict[str, Any]]
    artifacts: List[Dict[str, Any]]
    previousReleaseFingerprint: str
    previousResourceVersionIds: Dict[str, str]
    previousResourceRevisions: Dict[str, str]
    allowedResourceKeys: List[str]
    requireChangedResourceRevision: Literal[True]
    createdAt: str


class ProjectDeliveryExecutionBindings(TypedDict, total=False):
    releaseAuthorizationId: str
    releaseAuthorizationEvidenceFingerprint: str
    releaseAuthorizationReleaseFingerprint: str
    repairAttemptCount: int
    repairStatus: Literal[
        "queued",
        "running",
        "passed",
        "failed",
        "exhausted",
    ]
    repairEpisode: ProjectDeliveryRepairEpisode


class ProjectDeliveryExecutionEvent(TypedDict, total=False):
    id: str
    type: str
    stageId: Optional[ProjectDeliveryStageId]
    actorUserId: Optional[str]
    payload: Dict[str, Any]
    createdAt: str


class ProjectDeliveryExecution(TypedDict, total=False):
    id: str
    deliveryPlanId: str
    projectId: str
    userId: str
    organizationId: Optional[str]
    createdByUserId: Optional[str]
    planRevision: int
    schemaVersion: Literal[
        "computer_agents_project_delivery_execution_v1",
        "computer_agents_project_delivery_execution_v2",
    ]
    status: ProjectDeliveryExecutionStatus
    currentStage: Optional[ProjectDeliveryStageId]
    stages: Dict[ProjectDeliveryStageId, ProjectDeliveryStageState]
    bindings: ProjectDeliveryExecutionBindings
    costUsd: float
    budgetUsd: float
    executionAttempt: int
    nextReconcileAt: str
    lastError: Optional[str]
    startedAt: Optional[str]
    completedAt: Optional[str]
    createdAt: str
    updatedAt: str
    events: List[ProjectDeliveryExecutionEvent]


ProjectDeliveryArchetype = Literal[
    "agent",
    "scheduled_pipeline",
    "event_driven_pipeline",
    "service_topology",
]


class ProjectDeliveryDesignRequest(TypedDict, total=False):
    schemaVersion: Literal["computer_agents_project_delivery_design_request_v1"]
    brief: Dict[str, Any]
    validationAssets: List[ProjectDeliveryValidationAsset]
    capabilities: Dict[str, Any]
    topology: Dict[str, Any]
    bindings: Dict[str, Optional[str]]
    tests: Dict[str, List[Dict[str, Any]]]
    evaluation: Dict[str, Any]
    controls: Dict[str, Any]
    acceptance: Dict[str, Any]
    budget: Dict[str, float]


class ProjectDeliveryDesignIssue(TypedDict):
    code: str
    path: str
    message: str
    blocking: Literal[True]


class ProjectDeliveryDesignResult(TypedDict, total=False):
    schemaVersion: Literal["computer_agents_project_delivery_design_v1"]
    requestFingerprint: str
    designFingerprint: str
    readiness: Literal["ready", "needs_input"]
    archetype: ProjectDeliveryArchetype
    missingInputs: List[ProjectDeliveryDesignIssue]
    assumptions: List[str]
    proposedTopology: Dict[str, List[Dict[str, Any]]]
    contract: Optional[ProjectDeliveryContract]
    preview: Optional[ProjectDeliveryPreview]


class ProjectDeliveryDesignEvent(TypedDict):
    id: str
    type: str
    actorUserId: Optional[str]
    payload: Dict[str, Any]
    createdAt: str


class ProjectDeliveryDesign(TypedDict, total=False):
    id: str
    projectId: str
    userId: str
    organizationId: Optional[str]
    createdByUserId: Optional[str]
    revision: int
    status: Literal["needs_input", "ready", "archived"]
    requestFingerprint: str
    designFingerprint: str
    request: ProjectDeliveryDesignRequest
    design: ProjectDeliveryDesignResult
    idempotencyKey: Optional[str]
    createdAt: str
    updatedAt: str
    events: List[ProjectDeliveryDesignEvent]


OptimizationCampaignTargetKind = Literal["function", "metronome"]
OptimizationCampaignStatus = Literal[
    "draft",
    "queued",
    "producing",
    "evaluating",
    "awaiting_assurance",
    "ready_to_promote",
    "releasing",
    "completed",
    "plateaued",
    "failed",
    "cancelled",
]
OptimizationCampaignAttemptStatus = Literal[
    "queued",
    "producing",
    "evaluating",
    "awaiting_assurance",
    "accepted",
    "promoted",
    "rejected",
    "failed",
    "cancelled",
]


class OptimizationCampaignContract(TypedDict, total=False):
    schemaVersion: Literal["computer_agents_optimization_campaign_v1"]
    name: str
    projectId: Optional[str]
    objective: Dict[str, Any]
    target: Dict[str, Any]
    producer: Dict[str, Any]
    evidence: Dict[str, Any]
    limits: Dict[str, Any]
    publication: Dict[str, Any]
    idempotencyKey: str


class OptimizationCampaignAttempt(TypedDict, total=False):
    id: str
    campaignId: str
    attemptNumber: int
    status: OptimizationCampaignAttemptStatus
    producerRequest: Dict[str, Any]
    candidateId: Optional[str]
    candidateVersionId: Optional[str]
    candidateFingerprint: Optional[str]
    testRunId: Optional[str]
    evaluationRunId: Optional[str]
    assuranceRunId: Optional[str]
    acceptanceFingerprint: Optional[str]
    score: Optional[float]
    passRate: Optional[float]
    improvement: Optional[float]
    costUsd: float
    error: Optional[str]
    startedAt: Optional[str]
    completedAt: Optional[str]
    createdAt: str
    updatedAt: str


class OptimizationCampaignEvent(TypedDict):
    id: str
    type: str
    actorUserId: Optional[str]
    payload: Dict[str, Any]
    createdAt: str


class OptimizationCampaign(TypedDict, total=False):
    id: str
    userId: str
    organizationId: Optional[str]
    createdByUserId: Optional[str]
    projectId: Optional[str]
    name: str
    contract: OptimizationCampaignContract
    contractFingerprint: str
    objectiveFingerprint: str
    targetKind: OptimizationCampaignTargetKind
    targetResourceId: str
    baseVersionId: str
    baseFingerprint: str
    baselineEvaluationRunId: str
    baselineScore: float
    baselinePassRate: float
    status: OptimizationCampaignStatus
    attemptCount: int
    bestCandidateId: Optional[str]
    bestCandidateVersionId: Optional[str]
    bestScore: Optional[float]
    costUsd: float
    idempotencyKey: str
    startedAt: Optional[str]
    completedAt: Optional[str]
    cancelledAt: Optional[str]
    createdAt: str
    updatedAt: str
    attempts: List[OptimizationCampaignAttempt]
    events: List[OptimizationCampaignEvent]


ReleaseTargetKind = Literal["function", "metronome"]
ReleaseAction = Literal["publish", "publish_and_deploy"]
ReleaseStatus = Literal[
    "queued",
    "promoting",
    "ready_for_deployment",
    "deploying",
    "released",
    "failed",
    "cancelled",
]


class ReleaseRequest(TypedDict):
    schemaVersion: Literal["computer_agents_release_request_v1"]
    target: Dict[str, Any]
    candidate: Dict[str, str]
    action: ReleaseAction
    projectId: Optional[str]
    idempotencyKey: str


class ReleaseDeploymentRequest(TypedDict):
    method: Literal["POST"]
    path: str
    body: Dict[str, str]


class ReleaseEvent(TypedDict):
    sequence: int
    id: str
    type: str
    actorUserId: Optional[str]
    payload: Dict[str, Any]
    createdAt: str


class Release(TypedDict, total=False):
    id: str
    object: Literal["release"]
    projectId: Optional[str]
    target: Dict[str, str]
    candidate: Dict[str, str]
    assurance: Dict[str, str]
    action: ReleaseAction
    status: ReleaseStatus
    idempotencyKey: str
    requestFingerprint: str
    evidenceFingerprint: str
    revision: int
    deployment: Dict[str, Any]
    deploymentRequest: Optional[ReleaseDeploymentRequest]
    error: Optional[Dict[str, Optional[str]]]
    promotedAt: Optional[str]
    completedAt: Optional[str]
    createdAt: str
    updatedAt: str
    events: List[ReleaseEvent]


class ProjectDeliveryReleaseRequest(TypedDict):
    schemaVersion: Literal[
        "computer_agents_project_delivery_release_request_v1"
    ]
    deliveryExecutionId: str
    idempotencyKey: str


class ProjectDeliveryReleaseAuthorization(TypedDict, total=False):
    id: str
    object: Literal["project_delivery_release_authorization"]
    status: Literal["authorized"]
    projectId: str
    deliveryPlanId: str
    deliveryExecutionId: str
    planRevision: int
    contractFingerprint: str
    releaseFingerprint: str
    topologyCandidate: Optional[Dict[str, str]]
    assurance: Dict[str, str]
    idempotencyKey: str
    requestFingerprint: str
    evidenceFingerprint: str
    candidateExecutions: List[Dict[str, Any]]
    authorizedAt: str
    createdAt: str
    events: List[ReleaseEvent]


ProjectDeliveryPromotionStatus = Literal[
    "ready_for_deployment",
    "ready_for_activation",
    "activating",
    "released",
    "failed",
    "cancelled",
]

ProjectDeliveryPromotionResourceStatus = Literal[
    "pending",
    "deploying",
    "staged",
    "activated",
    "failed",
    "cancelled",
]


class ProjectDeliveryPromotion(TypedDict, total=False):
    id: str
    object: Literal["project_delivery_release_promotion"]
    status: ProjectDeliveryPromotionStatus
    authorizationId: str
    topologyCandidateId: str
    projectId: str
    deliveryExecutionId: str
    candidateManifestFingerprint: str
    releaseFingerprint: str
    authorizationEvidenceFingerprint: str
    idempotencyKey: str
    requestFingerprint: str
    receiptFingerprint: Optional[str]
    revision: int
    error: Optional[Dict[str, Optional[str]]]
    activationStartedAt: Optional[str]
    completedAt: Optional[str]
    createdAt: str
    updatedAt: str
    resources: List[Dict[str, Any]]
    events: List[ReleaseEvent]


class ProjectDeliveryPromotionReceipt(TypedDict):
    schemaVersion: Literal[
        "computer_agents_project_delivery_promotion_receipt_v2"
    ]
    promotionId: str
    authorizationId: str
    topologyCandidateId: str
    candidateManifestFingerprint: str
    releaseFingerprint: str
    authorizationEvidenceFingerprint: str
    resources: List[Dict[str, Any]]
    activatedAt: str


class ProjectOwnerCandidate(ProjectOwner, total=False):
    pass


ProjectUpdateStatus = Literal["on_track", "at_risk", "off_track", "complete"]
ProjectUpdateKind = Literal["update", "comment"]


class ProjectUpdateAttachment(TypedDict, total=False):
    id: str
    filename: str
    mimeType: str
    size: int
    url: str
    previewUrl: str
    workspacePath: str
    sourcePath: str
    environmentId: str


class _ProjectUpdateCommentRequired(TypedDict):
    id: str
    body: str
    attachments: List[ProjectUpdateAttachment]
    replies: List["ProjectUpdateComment"]
    author: ProjectOwner
    createdAt: str
    updatedAt: str


class ProjectUpdateComment(_ProjectUpdateCommentRequired, total=False):
    parentCommentId: str


class ProjectUpdateReaction(TypedDict):
    emoji: str
    userIds: List[str]
    count: int


class ProjectUpdate(TypedDict):
    id: str
    body: str
    kind: ProjectUpdateKind
    status: ProjectUpdateStatus
    attachments: List[ProjectUpdateAttachment]
    comments: List[ProjectUpdateComment]
    reactions: List[ProjectUpdateReaction]
    author: ProjectOwner
    createdAt: str
    updatedAt: str


class CreateProjectUpdateParams(TypedDict, total=False):
    body: str
    kind: ProjectUpdateKind
    status: ProjectUpdateStatus
    attachments: List[ProjectUpdateAttachment]
    idempotencyKey: str
    mentions: List[ProjectMentionReference]


class CreateProjectUpdateCommentParams(TypedDict, total=False):
    body: str
    attachments: List[ProjectUpdateAttachment]
    idempotencyKey: str
    parentCommentId: str
    replyToCommentId: str
    mentions: List[ProjectMentionReference]


class UpdateProjectUpdateCommentParams(TypedDict):
    body: str


class ProjectUpdateCommentResult(TypedDict):
    comment: ProjectUpdateComment
    update: ProjectUpdate
    project: Project


class DeleteProjectUpdateCommentResult(TypedDict):
    deletedCommentId: str
    update: ProjectUpdate
    project: Project


class ProjectUpdateReactionResult(TypedDict):
    selected: bool
    reaction: Optional[ProjectUpdateReaction]
    update: ProjectUpdate
    project: Project


class ProjectUpdateListResult(TypedDict):
    data: List[ProjectUpdate]
    hasMore: bool
    total: int


class ProjectUpdateResult(TypedDict, total=False):
    update: ProjectUpdate
    project: Project
    summary: ProjectSummary


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
    organizationId: Optional[str]
    createdByUserId: Optional[str]
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
    baseImage: str
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
    documentation: List[str]
    internetAccess: bool
    isDefault: bool
    computeProfile: EnvironmentComputeProfileId
    baseImage: str
    guiEnabled: bool
    officeAppsEnabled: bool
    metadata: EnvironmentMetadata


CreateComputerParams = CreateEnvironmentParams
UpdateComputerParams = UpdateEnvironmentParams


class ContainerStatus(TypedDict, total=False):
    status: Literal["running", "stopped"]
    containerId: str
    startedAt: str
    lastUsedAt: str
    executionCount: int
    message: str


class BuildTriggerResult(TypedDict):
    message: str
    environmentId: str
    buildStatus: Literal["building"]


class BuildStatusResult(TypedDict, total=False):
    buildStatus: BuildStatus
    imageTag: Optional[str]
    lastBuildAt: Optional[str]
    buildError: Optional[str]


class BuildLogsResult(TypedDict, total=False):
    buildLogs: str
    buildStatus: Optional[BuildStatus]


class TestBuildResult(TypedDict, total=False):
    success: bool
    imageTag: str
    message: str
    error: str


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


class StartContainerCustomSkillCodeFile(TypedDict, total=False):
    name: str
    content: str
    language: str


class StartContainerCustomSkill(TypedDict, total=False):
    id: str
    name: str
    description: str
    markdown: str
    codeFiles: List[StartContainerCustomSkillCodeFile]


class StartContainerParams(TypedDict, total=False):
    agentId: str
    enabledSkills: Dict[str, List[StartContainerCustomSkill]]
    customSkills: List[StartContainerCustomSkill]


class StartContainerResult(TypedDict):
    status: Literal["running"]
    containerId: str
    message: str


class StopContainerResult(TypedDict):
    status: Literal["stopped"]
    message: str


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


class TeamExecutionMemberMetadata(TypedDict):
    agentId: str
    agentName: str
    claudeAgentName: str


class TeamExecutionMetadata(TypedDict):
    mode: Literal["team"]
    teamAgentId: str
    teamAgentName: str
    orchestrator: TeamExecutionMemberMetadata
    subagents: List[TeamExecutionMemberMetadata]


class ThreadSubagentActivitySummary(TypedDict):
    agentId: str
    agentName: str
    claudeAgentName: str
    eventCount: int
    lastActiveAt: Optional[str]
    teamAgentId: str
    teamAgentName: str


class ThreadMessage(TypedDict, total=False):
    id: str
    threadId: str
    role: Literal["user", "assistant", "system", "execution_log"]
    content: str
    createdAt: str
    inputTokens: Optional[int]
    outputTokens: Optional[int]
    durationMs: Optional[int]
    actionsCount: Optional[int]
    logType: Optional[str]
    logLevel: Optional[Literal["info", "warn", "error", "success", "warning"]]
    logMetadata: Optional[Dict[str, Any]]


class Thread(TypedDict, total=False):
    id: str
    userId: str
    organizationId: Optional[str]
    createdByUserId: Optional[str]
    projectId: str
    environmentId: str
    agentId: str
    appId: Optional[str]
    contextId: Optional[str]
    contextName: Optional[str]
    task: Optional[str]
    title: str
    status: ThreadStatus
    messages: List[ThreadMessage]
    messageCount: int
    totalTokens: int
    totalCost: float
    totalCostUsd: float
    agentCost: float
    agentCostUsd: float
    environmentCost: float
    environmentCostUsd: float
    totalCT: int
    agentCT: int
    environmentCT: int
    inputTokens: int
    outputTokens: int
    cacheTokens: int
    environmentMinutes: Optional[float]
    environmentStorageGB: Optional[float]
    attachments: Optional[List[Dict[str, Any]]]
    lastMessageAt: Optional[str]
    lastMessagePreview: Optional[str]
    metadata: Optional[Dict[str, Any]]
    environmentName: Optional[str]
    agentName: Optional[str]
    agentPhotoUrl: Optional[str]
    agentAvatarUrl: Optional[str]
    teamExecution: TeamExecutionMetadata
    subagentActivity: List[ThreadSubagentActivitySummary]
    startedAt: Optional[str]
    completedAt: Optional[str]
    duration: Optional[str]
    createdAt: str
    updatedAt: str
    deletedAt: str
    queuedInBatch: bool
    batchJobId: str
    admissionReason: str


class CreateThreadParams(TypedDict, total=False):
    projectId: Optional[str]
    environmentId: str
    agentId: str
    title: str
    appId: Optional[str]
    messages: List[ThreadMessage]
    content: str
    task: str
    stream: Literal[False]
    schedule: Dict[str, Any]
    attachments: List[Dict[str, Any]]
    githubRepo: Dict[str, Any]
    metadata: Optional[Dict[str, Any]]
    messageMetadata: Optional[Dict[str, Any]]
    idempotencyKey: str
    queueWhenCapacityUnavailable: bool
    knowledgeContext: Dict[str, Any]


class UpdateThreadParams(TypedDict, total=False):
    title: str
    status: ThreadStatus
    agentId: Optional[str]
    projectId: Optional[str]


class ListThreadsParams(TypedDict, total=False):
    limit: int
    offset: int
    projectId: Optional[str]
    environmentId: str
    agentId: str
    appId: str
    scheduleId: str
    status: ThreadStatus
    createdAfter: str


class CopyThreadParams(TypedDict, total=False):
    title: str
    truncateAtMessageIndex: int
    environmentName: str
    environmentTarget: Literal["existing_environment", "new_forked_environment"]
    environmentStrategy: Literal["reuse_current", "forked_environment"]
    targetEnvironmentId: str
    fileCopyMode: Literal["all", "thread_only", "none"]


class ThreadCopyResponse(TypedDict, total=False):
    thread: Thread
    environmentId: str
    environmentName: str
    snapshotId: Optional[str]
    messagesCopied: int
    forkMode: Literal["latest", "historical", "current_environment", "existing_environment"]


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
    createdAt: Optional[str]
    time: Optional[str]
    message: str
    type: Literal["info", "error", "success", "warning"]
    eventType: Optional[str]
    isUserMessage: bool
    isReasoning: bool
    isActionSummary: bool
    isPlanning: bool
    isLLMResponse: bool
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

TaskStatus = Literal["backlog", "todo", "in_progress", "blocked", "in_review", "done", "canceled"]
TaskPriority = Literal["low", "medium", "high", "urgent"]
TaskType = Literal["task", "subtask", "loop"]
TaskCommentAuthorType = Literal["user", "agent", "system"]
TaskSprintStatus = Literal["planned", "active", "completed"]
TaskReleaseStatus = Literal["planned", "active", "completed"]


class TaskLoopParams(TypedDict, total=False):
    enabled: bool
    goal: str
    endGoal: str
    progressSignal: str
    verificationCriteria: str
    successCriteria: str
    maxIterations: int
    noProgressLimit: int
    minimumScore: float
    maxDurationMinutes: int
    regressionPolicy: Literal["continue", "stop"]
    workerAgentId: Optional[str]
    verifierAgentId: Optional[str]


TaskCreatorType = Literal["user", "agent"]


class TaskCreator(TypedDict, total=False):
    type: TaskCreatorType
    userId: Optional[str]
    agentId: Optional[str]
    name: Optional[str]
    avatarUrl: Optional[str]


class Task(TypedDict, total=False):
    object: Literal["task"]
    id: str
    userId: str
    organizationId: Optional[str]
    createdByUserId: Optional[str]
    creator: Optional[TaskCreator]
    projectId: Optional[str]
    releaseId: Optional[str]
    sprintId: Optional[str]
    title: str
    description: str
    status: TaskStatus
    priority: TaskPriority
    type: TaskType
    parentTaskId: Optional[str]
    loop: Optional[TaskLoopParams]
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
    loop: Optional[TaskLoopParams]
    sprintId: Optional[str]
    assigneeAgentId: Optional[str]
    creatorAgentId: Optional[str]
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
    loop: Optional[TaskLoopParams]
    review: Optional[Dict[str, Any]]
    linkedThreads: List[Thread]
    lastStartedThread: Optional[Thread]
    blockedByDependencyIds: List[str]
    readyToStart: bool


class TaskDetailResult(TypedDict, total=False):
    task: Task
    details: TaskDetails
    comments: List["TaskComment"]
    activity: List[Dict[str, Any]]


class TaskComment(TypedDict, total=False):
    object: Literal["task.comment"]
    id: str
    userId: str
    organizationId: Optional[str]
    createdByUserId: Optional[str]
    projectId: Optional[str]
    taskId: str
    task: Task
    body: str
    authorType: TaskCommentAuthorType
    authorAgentId: Optional[str]
    authorUserId: Optional[str]
    authorName: Optional[str]
    authorAvatarUrl: Optional[str]
    sourceThreadId: Optional[str]
    threadId: Optional[str]
    parentCommentId: Optional[str]
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
    parentCommentId: Optional[str]
    replyToCommentId: Optional[str]
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
    organizationId: Optional[str]
    createdByUserId: Optional[str]
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
    organizationId: Optional[str]
    createdByUserId: Optional[str]
    projectId: Optional[str]
    name: str
    description: str
    successCriteria: List[str]
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
    successCriteria: List[str]
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
    title: str
    environmentId: str
    agentId: str
    moveToInProgress: bool
    metadata: Optional[Dict[str, Any]]


class TaskStartThreadResult(TypedDict, total=False):
    thread: Thread
    task: Task
    subtasks: List[Task]
    agentSession: TaskAgentSession


class TaskRunThreadBatchParams(TypedDict, total=False):
    name: str
    description: str
    startPolicy: Literal["manual", "stay_on_shelf", "when_capacity_available"]
    definition: Dict[str, Any]
    metadata: Dict[str, Any]


class TaskRunThreadParams(TaskStartThreadParams, total=False):
    executionMode: Literal["blocking", "deferred"]
    idempotencyKey: str
    message: str
    content: str
    task: str
    queueWhenCapacityUnavailable: bool
    queueInBatch: bool
    batch: TaskRunThreadBatchParams


class TaskRunThreadResult(TaskStartThreadResult, total=False):
    executionStarted: bool
    idempotentReplay: bool
    queuedInBatch: bool
    batchJobId: Optional[str]
    batchJob: Dict[str, Any]
    execution: Dict[str, Any]


# ============================================================================
# Agent Config & Send Message
# ============================================================================

BuiltinAgentModel = Literal[
    "claude-opus-4-8",
    "claude-opus-4-7",
    "claude-opus-4-6",
    "claude-sonnet-4-5",
    "claude-haiku-4-5",
    "gpt-5.5-pro",
    "gpt-5.5",
    "gpt-5.4",
    "gpt-5.4-mini",
    "gpt-5.4-nano",
    "grok-4.5",
    "gemini-3-flash",
    "gemini-3-1-flash",
    "gemini-3-1-pro",
    "deepseek-v4-pro",
    "deepseek-v4-flash",
    "minimax-m3",
    "kimi-k2.6",
    "kimi-k2.7-code",
    "glm-5.2",
    "qwen3.5-397b-a17b",
    "qwen3.8-flash-next",
]
AgentModel = str
AgentExecutionEngine = Literal["computer-agents-cli", "native-claude", "grok-build"]
ReasoningEffort = Literal["minimal", "low", "medium", "high"]
DeepResearchModel = str


class AgentConfig(TypedDict, total=False):
    model: AgentModel
    instructions: str
    reasoningEffort: ReasoningEffort


class KnowledgeRetrievalContext(TypedDict, total=False):
    enabled: bool
    libraryIds: List[str]
    limit: int
    mode: Literal["read", "propose", "write"]
    source: str
    bindings: List[Dict[str, Any]]


class ThreadAttachmentReference(TypedDict, total=False):
    id: str
    filename: str
    mimeType: str
    size: int
    type: Literal["image", "document"]
    gcsPath: str
    url: Optional[str]
    workspacePath: Optional[str]
    integrationSource: Optional[str]
    githubRepoFullName: Optional[str]
    githubRef: Optional[str]
    githubItemPath: Optional[str]
    githubSelectionType: Optional[str]


class ThreadGitHubRepoReference(TypedDict, total=False):
    repoFullName: str
    repoName: str
    branch: str
    branchPrefix: str
    createPullRequests: bool
    forcePushCommits: bool


class SendMessageParams(TypedDict, total=False):
    content: str  # required
    task: str
    executionContent: str
    queueWhenCapacityUnavailable: bool
    knowledgeContext: KnowledgeRetrievalContext
    attachments: List[ThreadAttachmentReference]
    githubRepo: ThreadGitHubRepoReference
    quotedSelection: Dict[str, str]
    messageMetadata: Optional[Dict[str, Any]]
    researchModeEnabled: bool
    truncateAtMessageIndex: Optional[int]
    enabledSkills: List[str]
    editMessageId: Optional[str]
    persistFileChanges: bool
    reasoningEffort: ReasoningEffort
    mcpServers: List[McpServer]
    envVars: Dict[str, str]


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
PermissionResourceType = Literal[
    "agents", "skills", "servers", "computers", "files", "directories",
    "projects", "security_repositories",
]
PermissionSetSubjectType = Literal["agent", "human_user", "team", "project", "security_repository"]
PermissionRingId = Literal["ring_1", "ring_2", "ring_3"]
PermissionActionId = Literal[
    "workspace_read", "workspace_write", "local_shell", "local_skill_run",
    "external_read", "shared_resource_write", "send_email",
    "team_agent_delegation", "managed_resource_mutation", "public_deploy",
    "github_write", "payment_action", "public_message", "secret_export",
    "security_repository_view", "security_repository_findings_view",
    "security_repository_audit_view", "security_repository_run",
    "security_repository_triage", "security_repository_policy_manage",
    "security_repository_threat_model_manage",
    "security_repository_remediation_generate", "security_repository_risk_accept",
    "security_repository_remediation_publish", "security_repository_github_manage",
    "security_repository_access_manage", "security_repository_delete",
]


class PermissionRule(TypedDict, total=False):
    id: str
    targetId: str
    path: str
    access: PermissionAccessLevel
    note: str


class PermissionResourcePolicy(TypedDict, total=False):
    defaultAccess: PermissionAccessLevel
    rules: List[PermissionRule]


class PermissionRingPolicy(TypedDict, total=False):
    defaultAccess: PermissionAccessLevel


class PermissionActionPolicy(TypedDict, total=False):
    ringId: PermissionRingId
    access: PermissionAccessLevel


class PermissionSet(TypedDict, total=False):
    version: Literal[1]
    subjectType: PermissionSetSubjectType
    defaultAccess: PermissionAccessLevel
    rings: Dict[PermissionRingId, PermissionRingPolicy]
    actions: Dict[PermissionActionId, PermissionActionPolicy]
    resources: Dict[PermissionResourceType, PermissionResourcePolicy]


AgentBinary = Literal["Claude Code CLI"]
AgentVoiceMode = Literal["off", "web", "phone", "web_and_phone"]
AgentVoiceProvider = Literal["xai"]
AgentVoiceModel = str


class CloudAgent(TypedDict, total=False):
    id: str
    userId: str
    organizationId: Optional[str]
    createdByUserId: Optional[str]
    name: str
    description: str
    model: AgentModel
    instructions: str
    binary: AgentBinary
    executionEngine: AgentExecutionEngine
    reasoningEffort: ReasoningEffort
    enabledSkills: List[str]
    deepResearchModel: DeepResearchModel
    permissionSet: PermissionSet
    voiceMode: AgentVoiceMode
    voiceProvider: AgentVoiceProvider
    voiceModel: Optional[AgentVoiceModel]
    voiceId: Optional[str]
    voiceInstructions: Optional[str]
    voiceLanguageHint: Optional[str]
    voiceTurnDetection: Optional[Dict[str, Any]]
    voicePronunciationReplacements: Optional[Dict[str, Any]]
    metadata: Optional[Dict[str, Any]]
    createdAt: str
    updatedAt: str
    lastRunAt: Optional[str]
    isActive: bool
    isDefault: bool
    isSystem: bool


class CreateAgentParams(TypedDict, total=False):
    id: str
    name: str  # required
    description: str
    model: AgentModel  # required
    instructions: str
    binary: AgentBinary
    executionEngine: AgentExecutionEngine
    reasoningEffort: ReasoningEffort
    enabledSkills: List[str]
    deepResearchModel: DeepResearchModel
    permissionSet: PermissionSet
    voiceMode: AgentVoiceMode
    voiceProvider: AgentVoiceProvider
    voiceModel: Optional[AgentVoiceModel]
    voiceId: Optional[str]
    voiceInstructions: Optional[str]
    voiceLanguageHint: Optional[str]
    voiceTurnDetection: Optional[Dict[str, Any]]
    voicePronunciationReplacements: Optional[Dict[str, Any]]
    metadata: Dict[str, Any]
    isDefault: bool
    isSystem: bool


class UpdateAgentParams(TypedDict, total=False):
    name: str
    description: str
    model: AgentModel
    instructions: str
    binary: AgentBinary
    executionEngine: AgentExecutionEngine
    reasoningEffort: ReasoningEffort
    enabledSkills: List[str]
    deepResearchModel: DeepResearchModel
    permissionSet: Optional[PermissionSet]
    voiceMode: AgentVoiceMode
    voiceProvider: AgentVoiceProvider
    voiceModel: Optional[AgentVoiceModel]
    voiceId: Optional[str]
    voiceInstructions: Optional[str]
    voiceLanguageHint: Optional[str]
    voiceTurnDetection: Optional[Dict[str, Any]]
    voicePronunciationReplacements: Optional[Dict[str, Any]]
    metadata: Optional[Dict[str, Any]]


class AgentModelCatalogEntry(TypedDict, total=False):
    id: str
    label: str
    description: str
    intelligence: str
    contextWindow: str
    speed: str
    source: str
    providerType: Optional[str]
    requiredTier: str
    locked: bool


class AgentModelCatalogResponse(TypedDict):
    mode: Literal["managed_catalog", "deployment_fixed"]
    modelSelection: bool
    tier: str
    models: List[AgentModelCatalogEntry]


# ============================================================================
# Budget & Billing Types
# ============================================================================

class BudgetStatus(TypedDict, total=False):
    userId: str
    actorUserId: str
    organizationId: Optional[str]
    planId: str
    organizationPlan: Optional[Dict[str, Any]]
    balance: float
    balanceUsd: float
    totalSpent: float
    totalSpentUsd: float
    dailyLimit: float
    monthlyLimit: float
    tier: str
    subscriptionStatus: str
    subscriptionSource: str
    periodStartDate: Optional[str]
    periodEndDate: Optional[str]
    currentPeriodUsage: float
    usagePercentage: float
    tierQuota: float
    spent: float
    spentUsd: float
    currentPeriodUsageUsd: float
    limit: float
    limitUsd: float
    tierQuotaUsd: float
    includedTierQuota: float
    includedTierQuotaUsd: float
    remainingIncludedQuota: float
    remainingIncludedQuotaUsd: float
    remaining: float
    remainingUsd: float
    topUpBalance: float
    topUpBalanceUsd: float
    topUpTotalPurchased: float
    topUpTotalPurchasedUsd: float
    availableBudget: float
    availableBudgetUsd: float
    totalAvailableBudget: float
    totalAvailableBudgetUsd: float
    billingWallet: Optional[Dict[str, Any]]
    usageBillingEnabled: bool
    monthlyResourceSpendLimit: float
    monthlyResourceSpendLimitUsd: float
    pauseOnLimit: bool
    resourceEmailAlerts: bool
    monthlyResourceSpend: float
    monthlyResourceSpendUsd: float
    monthlyMeteredResourceUsage: float
    monthlyMeteredResourceUsageUsd: float
    createdAt: str
    updatedAt: str


class CanExecuteResult(TypedDict, total=False):
    canExecute: bool
    reason: str


class IncreaseBudgetParams(TypedDict, total=False):
    amountUsd: float  # required; ``amount`` remains accepted by the API for compatibility
    amount: float
    description: str


class IncreaseBudgetResult(TypedDict):
    success: bool
    userId: str
    actorUserId: str
    organizationId: Optional[str]
    addedAmount: float
    addedAmountUsd: float
    newBalance: float
    newBalanceUsd: float
    totalSpent: float
    totalSpentUsd: float


class BillingRecord(TypedDict, total=False):
    id: str
    userId: str
    organizationId: Optional[str]
    createdByUserId: Optional[str]
    threadId: Optional[str]
    recordType: Literal["charge", "credit", "refund"]
    type: Literal["execution", "credit", "mcp_usage", "adjustment"]
    amount: float
    amountUsd: float
    costUsd: float
    runId: str
    description: str
    metadata: Optional[Dict[str, Any]]
    createdAt: str


class ListBillingRecordsParams(TypedDict, total=False):
    limit: int
    offset: int


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
    totalCostUsd: float
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
    path: str
    type: Literal["file", "directory"]
    size: int
    lastModified: str
    hasChildren: Optional[bool]


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


class SendFilesToComputerParams(TypedDict, total=False):
    environmentId: str
    destinationEnvironmentId: str
    paths: list[str]


class MakeFilesAvailableToTeamParams(TypedDict, total=False):
    environmentId: str
    teamId: str
    paths: list[str]
    accessLevel: str


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


NotificationPreferenceKey = Literal[
    "agentRuns", "permissionRequests", "assignedWork", "taskActivity", "invitations", "productUpdates"
]
NotificationCategory = Literal[
    "agent_runs", "permission_requests", "assigned_work", "task_activity", "invitations", "product_updates"
]
NotificationSeverity = Literal["info", "success", "warning", "error", "critical"]
NotificationChannel = Literal["in_app", "push", "email", "webhook"]


class NotificationPreferenceDefinition(TypedDict):
    id: NotificationPreferenceKey
    category: NotificationCategory
    title: str
    description: str
    defaultEnabled: bool
    channels: List[NotificationChannel]


class NotificationEventDefinition(TypedDict):
    type: str
    preferenceKey: NotificationPreferenceKey
    category: NotificationCategory
    severity: NotificationSeverity
    defaultChannels: List[NotificationChannel]
    critical: bool
    digestible: bool


class NotificationCatalog(TypedDict):
    version: int
    preferences: List[NotificationPreferenceDefinition]
    events: List[NotificationEventDefinition]


class NotificationInboxItem(TypedDict, total=False):
    id: str
    eventId: str
    eventType: str
    recipientUserId: str
    organizationId: Optional[str]
    preferenceKey: NotificationPreferenceKey
    category: NotificationCategory
    severity: NotificationSeverity
    title: str
    body: str
    actionUrl: Optional[str]
    resourceType: Optional[str]
    resourceId: Optional[str]
    metadata: Dict[str, Any]
    seenAt: Optional[str]
    readAt: Optional[str]
    dismissedAt: Optional[str]
    archivedAt: Optional[str]
    actedAt: Optional[str]
    createdAt: str
    updatedAt: str


class NotificationInboxListResponse(TypedDict):
    data: List[NotificationInboxItem]
    nextCursor: Optional[str]


class NotificationInboxSummary(TypedDict):
    unread: int
    total: int


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

class GitCommitParams(TypedDict, total=False):
    message: str  # required
    path: str
    files: List[str]


class GitCommitResult(TypedDict):
    success: bool
    sha: str
    message: str


class GitPushParams(TypedDict, total=False):
    path: str
    branch: str


class GitPushResult(TypedDict):
    success: bool
    branch: str
    message: str


# ============================================================================
# Schedule Types
# ============================================================================

ScheduleType = Literal["one-time", "recurring"]


class Schedule(TypedDict, total=False):
    id: str
    userId: str
    organizationId: Optional[str]
    createdByUserId: Optional[str]
    projectId: str
    name: str
    description: str
    agentId: Optional[str]
    agentName: Optional[str]
    task: str
    workspaceId: str
    workspaceName: str
    contextId: str
    contextName: str
    environmentId: str
    environmentName: str
    appId: Optional[str]
    scheduleType: ScheduleType
    cronExpression: str
    scheduledTime: str
    timezone: str
    enabled: bool
    lastRunAt: str
    nextRunAt: str
    runCount: int
    successCount: int
    failureCount: int
    metadata: Dict[str, Any]
    createdAt: str
    updatedAt: str
    deletedAt: str


class ScheduleExecution(TypedDict, total=False):
    id: str
    scheduleId: str
    userId: str
    organizationId: Optional[str]
    createdByUserId: Optional[str]
    triggerType: Literal["automatic", "manual"]
    scheduledFor: str
    status: Literal["claimed", "running", "completed", "failed"]
    threadId: Optional[str]
    claimedBy: Optional[str]
    leaseExpiresAt: Optional[str]
    startedAt: Optional[str]
    completedAt: Optional[str]
    error: Optional[str]
    metadata: Optional[Dict[str, Any]]
    createdAt: str
    updatedAt: str
    threadTitle: Optional[str]
    threadStatus: Optional[str]
    threadCreatedAt: Optional[str]
    threadCompletedAt: Optional[str]
    threadLastMessagePreview: Optional[str]
    scheduleName: Optional[str]
    appId: Optional[str]
    contextId: Optional[str]


class ListScheduleExecutionsParams(TypedDict, total=False):
    scheduleId: str
    appId: str
    contextId: str
    rangeStart: str
    rangeEnd: str
    limit: int
    offset: int


class ScheduleTriggerResult(TypedDict):
    thread: Dict[str, Any]
    execution: ScheduleExecution
    message: str


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
    appId: str
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
    contextId: Optional[str]
    contextName: Optional[str]
    environmentId: Optional[str]
    environmentName: Optional[str]
    appId: Optional[str]
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
    userId: str
    organizationId: Optional[str]
    createdByUserId: Optional[str]
    name: str
    environmentId: str
    agentId: Optional[str]
    source: TriggerSource
    event: str
    filters: Dict[str, Any]
    action: TriggerAction
    enabled: bool
    webhookSecret: str
    webhookUrl: str
    lastTriggeredAt: Optional[str]
    createdAt: str
    updatedAt: str


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
    organizationId: Optional[str]
    createdByUserId: Optional[str]
    triggerId: str
    threadId: Optional[str]
    eventPayload: Optional[Dict[str, Any]]
    status: Literal["pending", "running", "completed", "failed"]
    error: Optional[str]
    createdAt: str


GitHubAutomationScopeType = Literal["organization", "project", "function", "web_app"]
GitHubAutomationKind = Literal[
    "security_scan", "pull_request_review", "deploy_function", "deploy_web_app"
]
GitHubAutomationExecutionStatus = Literal["queued", "running", "succeeded", "failed", "ignored"]


class GitHubAutomationConfiguration(TypedDict, total=False):
    events: List[str]
    branches: List[str]
    pathIncludes: List[str]
    pathExcludes: List[str]
    agentId: str
    environmentId: str
    instructions: str
    publishReview: bool


class GitHubAutomationBinding(TypedDict, total=False):
    id: str
    scopeType: GitHubAutomationScopeType
    scopeId: str
    organizationId: str
    userId: str
    createdByUserId: str
    repositoryFullName: str
    githubRepositoryExternalId: str
    githubInstallationExternalId: str
    kind: GitHubAutomationKind
    enabled: bool
    configuration: GitHubAutomationConfiguration
    createdAt: str
    updatedAt: str


class GitHubAutomationExecution(TypedDict, total=False):
    id: str
    bindingId: str
    organizationId: str
    deliveryId: str
    eventType: str
    action: str
    headSha: str
    status: GitHubAutomationExecutionStatus
    securityRunId: Optional[str]
    threadId: Optional[str]
    error: str
    metadata: Dict[str, Any]
    createdAt: str
    updatedAt: str
    completedAt: Optional[str]


class ListGitHubAutomationBindingsParams(TypedDict, total=False):
    scopeType: GitHubAutomationScopeType
    scopeId: str
    repositoryFullName: str


class CreateGitHubAutomationBindingParams(TypedDict, total=False):
    scopeType: GitHubAutomationScopeType
    scopeId: str
    repositoryFullName: str
    kind: GitHubAutomationKind
    enabled: bool
    configuration: GitHubAutomationConfiguration


class UpdateGitHubAutomationBindingParams(TypedDict, total=False):
    enabled: bool
    configuration: GitHubAutomationConfiguration


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
    userId: str
    organizationId: Optional[str]
    createdByUserId: Optional[str]
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
    status: Literal["draft", "active", "archived"]


class OrchestrationStepResult(TypedDict, total=False):
    stepId: str
    agentId: str
    status: Literal["pending", "running", "completed", "failed", "skipped"]
    output: str
    error: str
    durationMs: int


class OrchestrationRun(TypedDict, total=False):
    id: str
    organizationId: Optional[str]
    createdByUserId: Optional[str]
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
