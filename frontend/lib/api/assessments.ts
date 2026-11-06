import { apiClient, shouldUseMock } from "./client";
import type {
  AssessmentAttemptResponse,
  AssessmentResponse,
  AssessmentSummaryResultsResponse,
  AssessmentTopicResponse,
  CreateAssessmentRequest,
  QuestionPublicResponse,
  SubmitAnswerRequest,
  SubmitCodeRequest,
} from "@/types";

export async function listTopics(): Promise<AssessmentTopicResponse[]> {
  if (shouldUseMock("assessments")) {
    return [
      { id: "top-react", name: "React & Modern Frontend", description: "Hooks, patterns, virtual DOM, and component state." },
      { id: "top-ds", name: "Data Structures & Algorithms", description: "Arrays, maps, trees, graphs, and algorithmic complexity." },
      { id: "top-sys", name: "System Design & APIs", description: "REST, HTTP, databases, scalability, and system principles." },
    ];
  }
  return apiClient<AssessmentTopicResponse[]>("/assessment-topics", {
    method: "GET",
  });
}

export async function listQuestions(params?: {
  topic_id?: string;
  difficulty?: string;
  limit?: number;
}): Promise<QuestionPublicResponse[]> {
  if (shouldUseMock("assessments")) {
    return [
      {
        id: "q-1",
        topic_id: "top-react",
        prompt: "What is the primary purpose of the useCallback hook in React?",
        question_type: "multiple_choice",
        difficulty: "medium",
        options: [
          "Memoizing callback functions between renders",
          "Directly mutating DOM nodes",
          "Executing side-effects after rendering",
          "Managing global application state",
        ],
      },
    ];
  }
  return apiClient<QuestionPublicResponse[]>("/questions", {
    method: "GET",
    params,
  });
}

export async function createAssessment(data: CreateAssessmentRequest): Promise<AssessmentResponse> {
  if (shouldUseMock("assessments")) {
    const topics = data.selected_topics || ["React"];
    return {
      id: `as-${Date.now()}`,
      user_id: "mock_user_id",
      title: data.title || "Practice Assessment",
      mode: data.mode,
      selected_topics: topics,
      status: "in_progress",
      started_at: new Date().toISOString(),
      current_question: {
        id: "q-1",
        topic_id: topics[0] || "react",
        prompt: "What is the primary benefit of React Virtual DOM?",
        question_type: "multiple_choice",
        difficulty: "easy",
        options: [
          "Minimizing expensive real DOM manipulation operations",
          "Replacing the browser JavaScript engine entirely",
          "Storing private user credentials in state",
        ],
      },
    };
  }
  return apiClient<AssessmentResponse>("/assessments", {
    method: "POST",
    body: data,
  });
}

export async function listAssessments(): Promise<AssessmentResponse[]> {
  if (shouldUseMock("assessments")) {
    return [
      {
        id: "as-prev-1",
        user_id: "mock_user_id",
        title: "React Patterns Assessment",
        mode: "quiz",
        selected_topics: ["React"],
        status: "completed",
        started_at: new Date(Date.now() - 86400000).toISOString(),
        completed_at: new Date(Date.now() - 85000000).toISOString(),
        summary_result: { total_questions: 5, correct_answers: 4, average_score: 86.0 },
      },
    ];
  }
  return apiClient<AssessmentResponse[]>("/assessments", {
    method: "GET",
  });
}

export async function getAssessment(assessmentId: string): Promise<AssessmentResponse> {
  if (shouldUseMock("assessments")) {
    const list = await listAssessments();
    return list[0];
  }
  return apiClient<AssessmentResponse>(`/assessments/${assessmentId}`, {
    method: "GET",
  });
}

export async function submitAnswer(
  assessmentId: string,
  data: SubmitAnswerRequest
): Promise<AssessmentAttemptResponse> {
  if (shouldUseMock("assessments")) {
    return {
      id: `att-${Date.now()}`,
      assessment_id: assessmentId,
      question_id: data.question_id,
      is_correct: true,
      score: 100.0,
      feedback: "Correct! Good understanding of the concept.",
      created_at: new Date().toISOString(),
    };
  }
  return apiClient<AssessmentAttemptResponse>(`/assessments/${assessmentId}/answers`, {
    method: "POST",
    body: data,
  });
}

export async function runCode(
  assessmentId: string,
  data: SubmitCodeRequest
): Promise<{ status: string; passed_tests: number; total_tests: number; test_results?: unknown[]; error_message?: string }> {
  return apiClient<{ status: string; passed_tests: number; total_tests: number; test_results?: unknown[]; error_message?: string }>(
    `/assessments/${assessmentId}/run-code`,
    {
      method: "POST",
      body: data,
    }
  );
}

export async function submitCode(
  assessmentId: string,
  data: SubmitCodeRequest
): Promise<AssessmentAttemptResponse> {
  return apiClient<AssessmentAttemptResponse>(`/assessments/${assessmentId}/code-submissions`, {
    method: "POST",
    body: data,
  });
}

export async function getAssessmentResults(
  assessmentId: string
): Promise<AssessmentSummaryResultsResponse> {
  if (shouldUseMock("assessments")) {
    return {
      id: assessmentId,
      title: "React Patterns Assessment",
      mode: "quiz",
      status: "completed",
      total_questions: 5,
      correct_answers: 4,
      average_score: 86.0,
      completed_at: new Date().toISOString(),
      attempts: [],
    };
  }
  return apiClient<AssessmentSummaryResultsResponse>(`/assessments/${assessmentId}/results`, {
    method: "GET",
  });
}

export async function listAssessmentAttempts(): Promise<AssessmentAttemptResponse[]> {
  if (shouldUseMock("assessments")) {
    return [
      {
        id: "att-1",
        assessment_id: "as-1",
        question_id: "q-1",
        is_correct: true,
        score: 100.0,
        feedback: "Correct answer.",
        created_at: new Date().toISOString(),
      },
    ];
  }
  return apiClient<AssessmentAttemptResponse[]>("/assessment-attempts", {
    method: "GET",
  });
}
