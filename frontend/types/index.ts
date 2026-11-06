import type { components } from "./openapi";

export type Schemas = components["schemas"];

// Normalized API Error Envelope
export interface ApiErrorDetail {
  code: string;
  message: string;
  details?: Array<{
    location?: string;
    message?: string;
    type?: string;
    [key: string]: unknown;
  }> | unknown[];
}

export interface ApiErrorEnvelope {
  error: ApiErrorDetail;
}

// Auth Types
export type UserResponse = Schemas["UserResponse"];
export type UserLoginRequest = Schemas["UserLoginRequest"];
export type UserRegisterRequest = Schemas["UserRegisterRequest"];
export type TokenResponse = Schemas["TokenResponse"];

// Profile & Workspace Types
export type UserProfileResponse = Schemas["UserProfileResponse"];
export type UserProfileUpdate = Schemas["UserProfileUpdate"];
export type WorkspaceSummaryResponse = Schemas["WorkspaceSummaryResponse"];
export type ActivityResponse = Schemas["ActivityResponse"];
export type UserSettingsResponse = Schemas["UserSettingsResponse"];
export type UserSettingsUpdate = Schemas["UserSettingsUpdate"];

// Resume Types
export type ResumeResponse = Schemas["ResumeResponse"];
export type ResumeAnalysisResponse = Schemas["ResumeAnalysisResponse"];

// Skills & Capabilities Types
export type SkillResponse = Schemas["SkillResponse"];
export type UserCapabilityResponse = Schemas["UserCapabilityResponse"] & {
  mastery_score?: number | null;
};
export type EvidenceRecordResponse = Schemas["EvidenceRecordResponse"];
export type CreateEvidenceRequest = Schemas["CreateEvidenceRequest"];

// Assessment Types
export type AssessmentResponse = Schemas["AssessmentResponse"];
export type AssessmentTopicResponse = Schemas["AssessmentTopicResponse"];
export type QuestionPublicResponse = Schemas["QuestionPublicResponse"] & {
  title?: string | null;
  category?: string;
  subtopic?: string | null;
  difficulty_level?: number;
  programming_language?: string | null;
  starter_code?: string | null;
  starter_codes?: Record<string, string> | null;
  examples?: Array<{ input: string; output: string; explanation?: string }> | null;
  constraints?: string[];
  sample_test_cases?: Array<{ inputs: unknown[]; expected: unknown }>;
  schema_ddl?: string | null;
  validation_status?: string;
};
export type CreateAssessmentRequest = Schemas["CreateAssessmentRequest"];
export type SubmitAnswerRequest = Schemas["SubmitAnswerRequest"];
export type SubmitCodeRequest = Schemas["SubmitCodeRequest"];
export type AssessmentAttemptResponse = Schemas["AssessmentAttemptResponse"];
export type AssessmentSummaryResultsResponse = Schemas["AssessmentSummaryResultsResponse"] & {
  mastery_score?: number;
  mastery_band?: string;
  highest_tier_passed?: string;
  estimated_ability?: number;
};

// Project Types
export type ProjectAnalysisResponse = Schemas["ProjectAnalysisResponse"] & {
  major_features?: string[];
  technical_strengths?: string[];
  inspected_files?: string[];
  model_metadata?: {
    provider?: string;
    model?: string;
    note?: string;
  };
};
export type ProjectResponse = Schemas["ProjectResponse"] & {
  technologies?: string[];
  latest_analysis?: ProjectAnalysisResponse | null;
};
export type ProjectCreate = Omit<Schemas["ProjectCreate"], "technologies"> & {
  technologies?: string[];
};
export type ProjectUpdate = Omit<Schemas["ProjectUpdate"], "technologies"> & {
  technologies?: string[];
};
export type GitHubConnectResponse = Schemas["GitHubConnectResponse"];
export type GitHubRepoItem = Schemas["GitHubRepoItem"];
export type ImportGitHubRepoRequest = Schemas["ImportGitHubRepoRequest"];

// Goals & Placement Types
export type GoalResponse = Schemas["GoalResponse"];
export type GoalCreate = Schemas["GoalCreate"];
export type GoalUpdate = Schemas["GoalUpdate"];
export type JobMatchResponse = Schemas["JobMatchResponse"];
export type JobMatchCreate = Schemas["JobMatchCreate"];

// Roadmap Types
export type RoadmapResponse = Schemas["RoadmapResponse"];
export type RoadmapCreate = Schemas["RoadmapCreate"];
export type RoadmapUpdate = Schemas["RoadmapUpdate"];
export type MilestoneResponse = Schemas["MilestoneResponse"];
export type MilestoneCreate = Schemas["MilestoneCreate"];
export type MilestoneUpdate = Schemas["MilestoneUpdate"];

// Assistant Types
export type ConversationResponse = Schemas["ConversationResponse"];
export type ConversationSummaryResponse = Schemas["ConversationSummaryResponse"];
export type SendMessageRequest = Schemas["SendMessageRequest"];
export type MessageResponse = Schemas["MessageResponse"];

// UI Evidence Kind
export type EvidenceKind = "claimed" | "assessed" | "project";

