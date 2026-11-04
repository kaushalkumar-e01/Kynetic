import { apiClient, shouldUseMock } from "./client";
import type {
  MilestoneCreate,
  MilestoneResponse,
  MilestoneUpdate,
  RoadmapCreate,
  RoadmapResponse,
  RoadmapUpdate,
} from "@/types";

export async function createRoadmap(data: RoadmapCreate): Promise<RoadmapResponse> {
  if (shouldUseMock("roadmaps")) {
    return {
      id: `rm-${Date.now()}`,
      user_id: "mock_user_id",
      goal_id: data.goal_id,
      title: data.title,
      description: data.description,
      status: "active",
      progress_percentage: 0,
      milestones: [
        {
          id: "ms-1",
          user_id: "mock_user_id",
          roadmap_id: `rm-${Date.now()}`,
          title: "Complete Advanced React Quiz",
          description: "Solidify knowledge of React patterns and component lifecycles.",
          ordering: 1,
          status: "pending",
          resources: [{ title: "React Documentation", url: "https://react.dev" }],
          created_at: new Date().toISOString(),
        },
      ],
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    };
  }
  return apiClient<RoadmapResponse>("/roadmaps", {
    method: "POST",
    body: data,
  });
}

export async function listRoadmaps(): Promise<RoadmapResponse[]> {
  if (shouldUseMock("roadmaps")) {
    return [
      {
        id: "rm-1",
        user_id: "mock_user_id",
        title: "Frontend Engineering Mastery",
        description: "Milestones covering React, TypeScript, state management, and performance.",
        status: "active",
        progress_percentage: 40,
        milestones: [
          {
            id: "ms-1",
            user_id: "mock_user_id",
            roadmap_id: "rm-1",
            title: "Advanced React Patterns",
            description: "Custom hooks, compound components, render props.",
            ordering: 1,
            resources: [],
            status: "completed",
            created_at: new Date().toISOString(),
          },
          {
            id: "ms-2",
            user_id: "mock_user_id",
            roadmap_id: "rm-1",
            title: "TypeScript Generics & Utility Types",
            description: "Deep dive into conditional types, mapped types, and strict mode.",
            ordering: 2,
            resources: [],
            status: "completed",
            created_at: new Date().toISOString(),
          },
          {
            id: "ms-3",
            user_id: "mock_user_id",
            roadmap_id: "rm-1",
            title: "Full-Stack Project Capstone",
            description: "Deploy a production-ready application with CI/CD.",
            ordering: 3,
            resources: [],
            status: "pending",
            created_at: new Date().toISOString(),
          },
        ],
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      },
    ];
  }
  return apiClient<RoadmapResponse[]>("/roadmaps");
}

export async function getRoadmap(id: string): Promise<RoadmapResponse> {
  if (shouldUseMock("roadmaps")) {
    const list = await listRoadmaps();
    const found = list.find((r) => r.id === id);
    if (found) return found;
    return list[0];
  }
  return apiClient<RoadmapResponse>(`/roadmaps/${id}`);
}

export async function updateRoadmap(id: string, data: RoadmapUpdate): Promise<RoadmapResponse> {
  if (shouldUseMock("roadmaps")) {
    return {
      id,
      user_id: "mock_user_id",
      title: data.title || "Updated Roadmap",
      status: data.status || "active",
      progress_percentage: 50,
      milestones: [],
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    };
  }
  return apiClient<RoadmapResponse>(`/roadmaps/${id}`, {
    method: "PATCH",
    body: data,
  });
}

export async function deleteRoadmap(id: string): Promise<{ message: string }> {
  if (shouldUseMock("roadmaps")) {
    return { message: "Roadmap deleted successfully." };
  }
  return apiClient<{ message: string }>(`/roadmaps/${id}`, {
    method: "DELETE",
  });
}

export async function addMilestone(roadmapId: string, data: MilestoneCreate): Promise<MilestoneResponse> {
  if (shouldUseMock("roadmaps")) {
    return {
      id: `ms-${Date.now()}`,
      user_id: "mock_user_id",
      roadmap_id: roadmapId,
      title: data.title,
      description: data.description,
      ordering: data.ordering || 1,
      resources: data.resources || [],
      status: "pending",
      due_date: data.due_date,
      created_at: new Date().toISOString(),
    };
  }
  return apiClient<MilestoneResponse>(`/roadmaps/${roadmapId}/milestones`, {
    method: "POST",
    body: data,
  });
}

export async function updateMilestone(
  roadmapId: string,
  milestoneId: string,
  data: MilestoneUpdate
): Promise<MilestoneResponse> {
  if (shouldUseMock("roadmaps")) {
    return {
      id: milestoneId,
      user_id: "mock_user_id",
      roadmap_id: roadmapId,
      title: data.title || "Updated Milestone",
      description: data.description,
      status: data.status || "completed",
      resources: [],
      ordering: 1,
      created_at: new Date().toISOString(),
    };
  }
  return apiClient<MilestoneResponse>(`/roadmaps/${roadmapId}/milestones/${milestoneId}`, {
    method: "PATCH",
    body: data,
  });
}
