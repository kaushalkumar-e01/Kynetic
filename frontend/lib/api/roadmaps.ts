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
        description: "Path from foundational React knowledge to proficient portfolio development.",
        status: "active",
        progress_percentage: 60,
        milestones: [
          {
            id: "ms-1",
            user_id: "mock_user_id",
            roadmap_id: "rm-1",
            title: "Pass React Patterns Assessment",
            description: "Demonstrate solid grasp of state management, custom hooks, and rendering optimization.",
            ordering: 1,
            status: "completed",
            resources: [],
            created_at: new Date().toISOString(),
          },
          {
            id: "ms-2",
            user_id: "mock_user_id",
            roadmap_id: "rm-1",
            title: "Connect and Analyze Portfolio Project",
            description: "Attach GitHub repository and verify tech stack implementation.",
            ordering: 2,
            status: "completed",
            resources: [],
            created_at: new Date().toISOString(),
          },
          {
            id: "ms-3",
            user_id: "mock_user_id",
            roadmap_id: "rm-1",
            title: "Close Systems Design Gap",
            description: "Complete an architectural case study or add caching/API layer to project.",
            ordering: 3,
            status: "in_progress",
            resources: [],
            created_at: new Date().toISOString(),
          },
        ],
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      },
    ];
  }
  return apiClient<RoadmapResponse[]>("/roadmaps", {
    method: "GET",
  });
}

export async function getRoadmap(roadmapId: string): Promise<RoadmapResponse> {
  if (shouldUseMock("roadmaps")) {
    const list = await listRoadmaps();
    return list.find((r) => r.id === roadmapId) || list[0];
  }
  return apiClient<RoadmapResponse>(`/roadmaps/${roadmapId}`, {
    method: "GET",
  });
}

export async function updateRoadmap(roadmapId: string, data: RoadmapUpdate): Promise<RoadmapResponse> {
  if (shouldUseMock("roadmaps")) {
    const current = await getRoadmap(roadmapId);
    return {
      ...current,
      title: data.title || current.title,
      description: data.description ?? current.description,
      status: data.status || current.status,
    };
  }
  return apiClient<RoadmapResponse>(`/roadmaps/${roadmapId}`, {
    method: "PATCH",
    body: data,
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
