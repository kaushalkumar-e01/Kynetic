import { apiClient, shouldUseMock } from "./client";
import type {
  ProjectAnalysisResponse,
  ProjectCreate,
  ProjectResponse,
  ProjectUpdate,
} from "@/types";
import { projects as mockProjects } from "@/lib/mocks/data";

export async function createProject(data: ProjectCreate): Promise<ProjectResponse> {
  if (shouldUseMock("projects")) {
    return {
      id: `proj-${Date.now()}`,
      user_id: "mock_user_id",
      name: data.name,
      description: data.description,
      source_type: data.source_type || "manual",
      repository_url: data.repository_url,
      created_at: new Date().toISOString(),
    };
  }
  return apiClient<ProjectResponse>("/projects", {
    method: "POST",
    body: data,
  });
}

export async function listProjects(): Promise<ProjectResponse[]> {
  if (shouldUseMock("projects")) {
    return mockProjects.map((p) => ({
      id: p.id,
      user_id: "mock_user_id",
      name: p.name,
      description: p.description,
      source_type: "manual",
      repository_url: `https://github.com/mayachen/${p.id}`,
      created_at: new Date().toISOString(),
      latest_analysis: {
        id: `ana-${p.id}`,
        project_id: p.id,
        user_id: "mock_user_id",
        status: "completed",
        purpose: "Product surfaces component system",
        detected_technologies: p.stack,
        architecture_summary: "Modular component hierarchy with state-driven transitions.",
        demonstrated_skills: ["React", "TypeScript", "Tailwind CSS"],
        missing_requirements: ["Automated unit test coverage"],
        recommendations: ["Add automated test suite", "Configure CI/CD workflow"],
        completed_at: new Date().toISOString(),
        created_at: new Date().toISOString(),
      },
    }));
  }
  return apiClient<ProjectResponse[]>("/projects", {
    method: "GET",
  });
}

export async function getProject(projectId: string): Promise<ProjectResponse> {
  if (shouldUseMock("projects")) {
    const list = await listProjects();
    const found = list.find((p) => p.id === projectId);
    return found || list[0];
  }
  return apiClient<ProjectResponse>(`/projects/${projectId}`, {
    method: "GET",
  });
}

export async function updateProject(projectId: string, data: ProjectUpdate): Promise<ProjectResponse> {
  if (shouldUseMock("projects")) {
    return {
      id: projectId,
      user_id: "mock_user_id",
      name: data.name || "Updated Project",
      description: data.description,
      source_type: "manual",
      repository_url: data.repository_url,
      created_at: new Date().toISOString(),
    };
  }
  return apiClient<ProjectResponse>(`/projects/${projectId}`, {
    method: "PATCH",
    body: data,
  });
}

export async function deleteProject(projectId: string): Promise<{ message: string }> {
  if (shouldUseMock("projects")) {
    return { message: "Project deleted (mock)." };
  }
  return apiClient<{ message: string }>(`/projects/${projectId}`, {
    method: "DELETE",
  });
}

export async function analyzeProject(projectId: string): Promise<ProjectAnalysisResponse> {
  if (shouldUseMock("projects")) {
    return {
      id: `ana-${Date.now()}`,
      project_id: projectId,
      user_id: "mock_user_id",
      status: "completed",
      purpose: "Analyzed code repository",
      detected_technologies: ["React", "TypeScript", "Tailwind CSS"],
      architecture_summary: "Component hierarchy with reactive state management",
      demonstrated_skills: ["React", "TypeScript", "Frontend Engineering"],
      missing_requirements: ["Integration testing"],
      recommendations: ["Add integration tests", "Include README architectural diagram"],
      completed_at: new Date().toISOString(),
      created_at: new Date().toISOString(),
    };
  }
  return apiClient<ProjectAnalysisResponse>(`/projects/${projectId}/analyze`, {
    method: "POST",
  });
}

export async function listProjectAnalyses(projectId: string): Promise<ProjectAnalysisResponse[]> {
  if (shouldUseMock("projects")) {
    const analysis = await analyzeProject(projectId);
    return [analysis];
  }
  return apiClient<ProjectAnalysisResponse[]>(`/projects/${projectId}/analyses`, {
    method: "GET",
  });
}

export async function getProjectAnalysis(analysisId: string): Promise<ProjectAnalysisResponse> {
  if (shouldUseMock("projects")) {
    return {
      id: analysisId,
      project_id: "mock_proj_id",
      user_id: "mock_user_id",
      status: "completed",
      purpose: "Web project analysis",
      detected_technologies: ["React", "TypeScript"],
      architecture_summary: "Component modularity",
      demonstrated_skills: ["React", "TypeScript"],
      missing_requirements: ["End-to-end tests"],
      recommendations: ["Improve test coverage"],
      completed_at: new Date().toISOString(),
      created_at: new Date().toISOString(),
    };
  }
  return apiClient<ProjectAnalysisResponse>(`/project-analyses/${analysisId}`, {
    method: "GET",
  });
}
