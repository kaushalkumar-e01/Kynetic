from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class AssessmentTopicResponse(BaseModel):
    id: str
    name: str
    description: Optional[str] = None

    class Config:
        from_attributes = True


class QuestionPublicResponse(BaseModel):
    id: str
    topic_id: str
    category: str = "cs_fundamentals"
    subtopic: Optional[str] = None
    question_type: str
    difficulty: str
    difficulty_level: int = 2
    programming_language: Optional[str] = None
    title: Optional[str] = None
    prompt: str
    options: List[str] = []
    starter_code: Optional[str] = None
    starter_codes: Optional[Dict[str, str]] = None
    examples: Optional[List[Dict[str, Any]]] = None
    constraints: Optional[List[str]] = None
    sample_test_cases: Optional[List[Dict[str, Any]]] = None
    schema_ddl: Optional[str] = None
    source_attribution: Optional[str] = None
    validation_status: str = "validated"

    class Config:
        from_attributes = True


class CreateAssessmentRequest(BaseModel):
    title: Optional[str] = None
    mode: str = Field("assessment", description="Mode: 'assessment' or 'practice'")
    selected_topics: List[str] = Field(default_factory=list, description="List of topic names to assess")


class SubmitAnswerRequest(BaseModel):
    question_id: str
    answer: str


class SubmitCodeRequest(BaseModel):
    question_id: str
    code: str


class AssessmentAttemptResponse(BaseModel):
    id: str
    assessment_id: str
    question_id: str
    is_correct: Optional[bool] = None
    score: float
    feedback: Optional[str] = None
    execution_result: Optional[Dict[str, Any]] = None
    created_at: datetime

    class Config:
        from_attributes = True


class AssessmentResponse(BaseModel):
    id: str
    user_id: str
    title: str
    mode: str
    selected_topics: List[str] = []
    status: str
    started_at: datetime
    completed_at: Optional[datetime] = None
    current_question: Optional[QuestionPublicResponse] = None
    summary_result: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True


class AssessmentSummaryResultsResponse(BaseModel):
    id: str
    title: str
    mode: str
    status: str
    total_questions: int
    correct_answers: int
    average_score: float
    mastery_score: Optional[float] = None
    mastery_band: Optional[str] = None
    highest_tier_passed: Optional[str] = None
    estimated_ability: Optional[float] = None
    completed_at: Optional[datetime] = None
    attempts: List[AssessmentAttemptResponse] = []


class QuestionBankStatsResponse(BaseModel):
    total_questions: int
    validated_questions: int
    by_category: Dict[str, int]
    by_difficulty: Dict[str, int]
    by_question_type: Dict[str, int]
    by_language: Dict[str, int]


class AIGenerateBatchRequest(BaseModel):
    skill_or_topic: str
    category: str = "cs_fundamentals"
    difficulty: str = "medium"
    question_type: str = "coding"
    batch_size: int = 10
    programming_language: Optional[str] = None


class AIGenerateBatchResponse(BaseModel):
    requested: int
    validated_and_saved: int
    rejected_count: int
    duplicates_prevented: int = 0
    validation_errors: List[str] = []
    topic: str
    model_metadata: Dict[str, Any]

