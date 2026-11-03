import { apiClient, shouldUseMock } from "./client";
import type {
  ActivityResponse,
  UserSettingsResponse,
  UserSettingsUpdate,
  WorkspaceSummaryResponse,
} from "@/types";
import { activities as mockActivities } from "@/lib/mocks/data";

export async function getWorkspaceSummary(): Promise<WorkspaceSummaryResponse> {
  if (shouldUseMock("workspace")) {
    return {
      user: {
        id: "mock_user_id",
        email: "maya.chen@example.com",
        account_status: "active",
        created_at: new Date().toISOString(),
      },
      profile: {
        id: "mock_profile_id",
        user_id: "mock_user_id",
        display_name: "Maya Chen",
        headline: "Product engineer",
        education_summary: "B.S. in Computer Science",
        experience_summary: "Frontend developer",
        preferred_domains: ["Frontend engineering"],
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      },
      resumes_count: 1,
      projects_count: 3,
      assessments_count: 2,
      goals_count: 2,
      roadmaps_count: 1,
      recent_activities: [
        {
          id: "act-1",
          activity_type: "assessment_completed",
          related_record_type: "assessment",
          details: { title: "React Patterns", score: 86 },
          created_at: new Date().toISOString(),
        },
      ],
      recent_goals: [{ id: "g-1", title: "Target Software Engineer", goal_type: "placement", status: "active" }],
      active_roadmap: { id: "rm-1", title: "Frontend Engineering Mastery", status: "active" },
    };
  }
  return apiClient<WorkspaceSummaryResponse>("/workspace/summary", {
    method: "GET",
  });
}

export async function getActivities(limit = 20): Promise<ActivityResponse[]> {
  if (shouldUseMock("workspace")) {
    return mockActivities.map((a, i) => ({
      id: `act-${i}`,
      activity_type: a.icon === "check" ? "assessment_completed" : a.icon === "git" ? "project_created" : "resume_uploaded",
      related_record_type: a.kind,
      details: { title: a.title, detail: a.detail, time: a.time },
      created_at: new Date().toISOString(),
    }));
  }
  return apiClient<ActivityResponse[]>("/activity", {
    method: "GET",
    params: { limit },
  });
}

export async function getSettings(): Promise<UserSettingsResponse> {
  if (shouldUseMock("workspace")) {
    return {
      email: "maya.chen@example.com",
      account_status: "active",
      learning_preferences: { theme: "dark", email_notifications: true },
    };
  }
  return apiClient<UserSettingsResponse>("/settings", {
    method: "GET",
  });
}

export async function updateSettings(data: UserSettingsUpdate): Promise<UserSettingsResponse> {
  if (shouldUseMock("workspace")) {
    return {
      email: "maya.chen@example.com",
      account_status: "active",
      learning_preferences: data.learning_preferences ?? {},
    };
  }
  return apiClient<UserSettingsResponse>("/settings", {
    method: "PATCH",
    body: data,
  });
}
