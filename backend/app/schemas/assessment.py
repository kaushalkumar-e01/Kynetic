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
    question_type: str
    difficulty: str
    prompt: str
    options: List[str] = []
    source_attribution: Optional[str] = None

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
    completed_at: Optional[datetime] = None
    attempts: List[AssessmentAttemptResponse] = []

