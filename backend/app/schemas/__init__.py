from app.schemas.health import HealthResponse
from app.schemas.common import ResponseEnvelope, PaginatedResponse
from app.schemas.auth import UserRegisterRequest, UserLoginRequest, UserResponse, TokenResponse
from app.schemas.profile import UserProfileResponse, UserProfileUpdate
from app.schemas.workspace import (
    ActivityResponse,
    WorkspaceSummaryResponse,
    UserSettingsResponse,
    UserSettingsUpdate,
)
from app.schemas.resume import ResumeResponse, ResumeAnalysisResponse
from app.schemas.skill import (
    SkillResponse,
    EvidenceRecordResponse,
    UserCapabilityResponse,
    CreateEvidenceRequest,
)
from app.schemas.assessment import (
    AssessmentTopicResponse,
    QuestionPublicResponse,
    CreateAssessmentRequest,
    SubmitAnswerRequest,
    SubmitCodeRequest,
    AssessmentAttemptResponse,
    AssessmentResponse,
    AssessmentSummaryResultsResponse,
)
from app.schemas.project import (
    ProjectCreate,
    ProjectUpdate,
    ProjectResponse,
    ProjectAnalysisResponse,
    GitHubConnectResponse,
    GitHubRepoItem,
    ImportGitHubRepoRequest,
)
from app.schemas.goal import (
    GoalCreate,
    GoalUpdate,
    GoalResponse,
    JobMatchCreate,
    JobMatchResponse,
    SkillMatchItem,
)
from app.schemas.roadmap import (
    RoadmapCreate,
    RoadmapUpdate,
    RoadmapResponse,
    MilestoneCreate,
    MilestoneUpdate,
    MilestoneResponse,
)
from app.schemas.assistant import (
    SendMessageRequest,
    MessageResponse,
    ConversationResponse,
    ConversationSummaryResponse,
)

__all__ = [
    "HealthResponse",
    "ResponseEnvelope",
    "PaginatedResponse",
    "UserRegisterRequest",
    "UserLoginRequest",
    "UserResponse",
    "TokenResponse",
    "UserProfileResponse",
    "UserProfileUpdate",
    "ActivityResponse",
    "WorkspaceSummaryResponse",
    "UserSettingsResponse",
    "UserSettingsUpdate",
    "ResumeResponse",
    "ResumeAnalysisResponse",
    "SkillResponse",
    "EvidenceRecordResponse",
    "UserCapabilityResponse",
    "CreateEvidenceRequest",
    "AssessmentTopicResponse",
    "QuestionPublicResponse",
    "CreateAssessmentRequest",
    "SubmitAnswerRequest",
    "SubmitCodeRequest",
    "AssessmentAttemptResponse",
    "AssessmentResponse",
    "AssessmentSummaryResultsResponse",
    "ProjectCreate",
    "ProjectUpdate",
    "ProjectResponse",
    "ProjectAnalysisResponse",
    "GitHubConnectResponse",
    "GitHubRepoItem",
    "ImportGitHubRepoRequest",
    "GoalCreate",
    "GoalUpdate",
    "GoalResponse",
    "JobMatchCreate",
    "JobMatchResponse",
    "SkillMatchItem",
    "RoadmapCreate",
    "RoadmapUpdate",
    "RoadmapResponse",
    "MilestoneCreate",
    "MilestoneUpdate",
    "MilestoneResponse",
    "SendMessageRequest",
    "MessageResponse",
    "ConversationResponse",
    "ConversationSummaryResponse",
]
