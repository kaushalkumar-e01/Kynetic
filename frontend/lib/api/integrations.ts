import { apiClient, shouldUseMock } from "./client";
import type {
  GitHubConnectResponse,
  GitHubRepoItem,
  ImportGitHubRepoRequest,
  ProjectResponse,
} from "@/types";

export async function getGitHubConnectUrl(): Promise<GitHubConnectResponse> {
  if (shouldUseMock("integrations")) {
    return {
      authorization_url: "https://github.com/login/oauth/authorize?client_id=mock_id&scope=repo",
      state: "mock_state_xyz",
    };
  }
  return apiClient<GitHubConnectResponse>("/integrations/github/connect", {
    method: "GET",
  });
}

export async function handleGitHubCallback(code: string): Promise<{ message: string; provider: string }> {
  if (shouldUseMock("integrations")) {
    return { message: "GitHub account connected (mock).", provider: "github" };
  }
  return apiClient<{ message: string; provider: string }>("/integrations/github/callback", {
    method: "GET",
    params: { code },
  });
}

export async function listGitHubRepositories(): Promise<GitHubRepoItem[]> {
  if (shouldUseMock("integrations")) {
    return [
      {
        name: "kinetic-ui",
        full_name: "mayachen/kinetic-ui",
        description: "A motion-first component system for accessible product surfaces.",
        html_url: "https://github.com/mayachen/kinetic-ui",
        language: "TypeScript",
        is_private: false,
        stargazers_count: 42,
        updated_at: new Date().toISOString(),
      },
      {
        name: "campus-circles",
        full_name: "mayachen/campus-circles",
        description: "Peer study groups with lightweight matching.",
        html_url: "https://github.com/mayachen/campus-circles",
        language: "JavaScript",
        is_private: false,
        stargazers_count: 12,
        updated_at: new Date().toISOString(),
      },
    ];
  }
  return apiClient<GitHubRepoItem[]>("/integrations/github/repositories", {
    method: "GET",
  });
}

export async function importGitHubRepository(data: ImportGitHubRepoRequest): Promise<ProjectResponse> {
  if (shouldUseMock("integrations")) {
    return {
      id: `proj-${Date.now()}`,
      user_id: "mock_user_id",
      name: data.name || "Imported Repository",
      description: data.description,
      source_type: "github",
      repository_url: data.repository_url,
      created_at: new Date().toISOString(),
    };
  }
  return apiClient<ProjectResponse>("/integrations/github/repositories", {
    method: "POST",
    body: data,
  });
}

export async function disconnectGitHub(): Promise<{ message: string }> {
  if (shouldUseMock("integrations")) {
    return { message: "GitHub connection removed (mock)." };
  }
  return apiClient<{ message: string }>("/integrations/github/connection", {
    method: "DELETE",
  });
}
