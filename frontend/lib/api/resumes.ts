import { apiClient, shouldUseMock } from "./client";
import type { ResumeAnalysisResponse, ResumeResponse } from "@/types";

export async function uploadResume(file: File): Promise<ResumeResponse> {
  if (shouldUseMock("resumes")) {
    return {
      id: "mock_resume_id",
      user_id: "mock_user_id",
      original_filename: file.name,
      file_size: file.size,
      mime_type: file.type || "application/pdf",
      status: "uploaded",
      created_at: new Date().toISOString(),
    };
  }

  const formData = new FormData();
  formData.append("file", file);

  return apiClient<ResumeResponse>("/resumes", {
    method: "POST",
    body: formData,
  });
}

export async function listResumes(): Promise<ResumeResponse[]> {
  if (shouldUseMock("resumes")) {
    return [
      {
        id: "mock_resume_id",
        user_id: "mock_user_id",
        original_filename: "Maya-Chen-Resume.pdf",
        file_size: 1048576,
        mime_type: "application/pdf",
        status: "uploaded",
        created_at: new Date().toISOString(),
        analysis: {
          id: "mock_analysis_id",
          resume_id: "mock_resume_id",
          user_id: "mock_user_id",
          status: "completed",
          extracted_profile: {
            education: [{ institution: "UC Berkeley", degree: "B.S. Computer Science", year: "2025" }],
            experience: [{ role: "Product Engineer Intern", company: "TechCorp", period: "Summer 2024" }],
            claimed_skills: [
              { name: "React", category: "framework" },
              { name: "TypeScript", category: "language" },
              { name: "Python", category: "language" },
              { name: "Systems Thinking", category: "concept" },
            ],
          },
          strengths: [
            "Strong foundation in modern frontend architecture and React.",
            "Demonstrated open-source contributions with clear repository evidence.",
          ],
          suggestions: [
            "Add concrete repository links or code submissions for Systems Thinking.",
            "Take the React patterns assessment to verify claimed proficiency.",
          ],
          completed_at: new Date().toISOString(),
          created_at: new Date().toISOString(),
        },
      },
    ];
  }
  return apiClient<ResumeResponse[]>("/resumes", {
    method: "GET",
  });
}

export async function getResume(resumeId: string): Promise<ResumeResponse> {
  if (shouldUseMock("resumes")) {
    const list = await listResumes();
    return list[0];
  }
  return apiClient<ResumeResponse>(`/resumes/${resumeId}`, {
    method: "GET",
  });
}

export async function deleteResume(resumeId: string): Promise<{ message: string }> {
  if (shouldUseMock("resumes")) {
    return { message: "Resume deleted (mock)." };
  }
  return apiClient<{ message: string }>(`/resumes/${resumeId}`, {
    method: "DELETE",
  });
}

export async function analyzeResume(resumeId: string): Promise<ResumeAnalysisResponse> {
  if (shouldUseMock("resumes")) {
    return {
      id: "mock_analysis_id",
      resume_id: resumeId,
      user_id: "mock_user_id",
      status: "completed",
      extracted_profile: {
        claimed_skills: [
          { name: "React", category: "framework" },
          { name: "TypeScript", category: "language" },
        ],
      },
      strengths: ["Clear technical project alignment with frontend roles."],
      suggestions: ["Take assessments to verify claimed capabilities."],
      completed_at: new Date().toISOString(),
      created_at: new Date().toISOString(),
    };
  }
  return apiClient<ResumeAnalysisResponse>(`/resumes/${resumeId}/analyze`, {
    method: "POST",
  });
}

export async function getResumeAnalysis(resumeId: string): Promise<ResumeAnalysisResponse> {
  if (shouldUseMock("resumes")) {
    return analyzeResume(resumeId);
  }
  return apiClient<ResumeAnalysisResponse>(`/resumes/${resumeId}/analysis`, {
    method: "GET",
  });
}
