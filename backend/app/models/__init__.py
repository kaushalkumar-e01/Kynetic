from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin
from app.models.user import User, UserProfile
from app.models.resume import Resume, ResumeAnalysis
from app.models.skill import Skill, EvidenceRecord, UserCapability
from app.models.assessment import AssessmentTopic, Question, Assessment, AssessmentAttempt
from app.models.project import Project, ProjectAnalysis, ConnectedAccount
from app.models.goal import Goal, JobMatch
from app.models.roadmap import Roadmap, RoadmapMilestone
from app.models.activity import UserActivity
from app.models.assistant import AssistantConversation, AssistantMessage

__all__ = [
    "Base",
    "TimestampMixin",
    "UUIDPrimaryKeyMixin",
    "User",
    "UserProfile",
    "Resume",
    "ResumeAnalysis",
    "Skill",
    "EvidenceRecord",
    "UserCapability",
    "AssessmentTopic",
    "Question",
    "Assessment",
    "AssessmentAttempt",
    "Project",
    "ProjectAnalysis",
    "ConnectedAccount",
    "Goal",
    "JobMatch",
    "Roadmap",
    "RoadmapMilestone",
    "UserActivity",
    "AssistantConversation",
    "AssistantMessage",
]

