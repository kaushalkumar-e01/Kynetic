import { apiClient, shouldUseMock } from "./client";
import type { GoalCreate, GoalResponse, GoalUpdate } from "@/types";

export async function createGoal(data: GoalCreate): Promise<GoalResponse> {
  if (shouldUseMock("goals")) {
    return {
      id: `g-${Date.now()}`,
      user_id: "mock_user_id",
      goal_type: data.goal_type,
      title: data.title,
      description: data.description,
      target_date: data.target_date,
      status: "active",
      created_at: new Date().toISOString(),
    };
  }
  return apiClient<GoalResponse>("/goals", {
    method: "POST",
    body: data,
  });
}

export async function listGoals(): Promise<GoalResponse[]> {
  if (shouldUseMock("goals")) {
    return [
      {
        id: "g-1",
        user_id: "mock_user_id",
        goal_type: "placement",
        title: "Target Frontend Engineer Role",
        description: "Prepare capabilities and evidence for summer internship interviews.",
        status: "active",
        target_date: "2025-06-01",
        created_at: new Date().toISOString(),
      },
      {
        id: "g-2",
        user_id: "mock_user_id",
        goal_type: "learning",
        title: "Master TypeScript & React Patterns",
        description: "Score >85% in advanced React assessments.",
        status: "active",
        created_at: new Date().toISOString(),
      },
    ];
  }
  return apiClient<GoalResponse[]>("/goals", {
    method: "GET",
  });
}

export async function getGoal(goalId: string): Promise<GoalResponse> {
  if (shouldUseMock("goals")) {
    const list = await listGoals();
    return list.find((g) => g.id === goalId) || list[0];
  }
  return apiClient<GoalResponse>(`/goals/${goalId}`, {
    method: "GET",
  });
}

export async function updateGoal(goalId: string, data: GoalUpdate): Promise<GoalResponse> {
  if (shouldUseMock("goals")) {
    return {
      id: goalId,
      user_id: "mock_user_id",
      goal_type: "placement",
      title: data.title || "Updated Goal",
      description: data.description,
      status: data.status || "active",
      target_date: data.target_date,
      created_at: new Date().toISOString(),
    };
  }
  return apiClient<GoalResponse>(`/goals/${goalId}`, {
    method: "PATCH",
    body: data,
  });
}

export async function deleteGoal(goalId: string): Promise<{ message: string }> {
  if (shouldUseMock("goals")) {
    return { message: "Goal deleted (mock)." };
  }
  return apiClient<{ message: string }>(`/goals/${goalId}`, {
    method: "DELETE",
  });
}
