import { apiClient, shouldUseMock } from "./client";
import type { UserProfileResponse, UserProfileUpdate } from "@/types";

export async function getProfile(): Promise<UserProfileResponse> {
  if (shouldUseMock("profile")) {
    return {
      id: "mock_profile_id",
      user_id: "mock_user_id",
      display_name: "Maya Chen",
      headline: "Product engineer & student",
      education_summary: "B.S. in Computer Science, UC Berkeley (2025)",
      experience_summary: "Frontend engineering intern, open source maintainer",
      preferred_domains: ["Frontend Engineering", "Design Systems", "Web Performance"],
      learning_preferences: { theme: "dark" },
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    };
  }
  return apiClient<UserProfileResponse>("/profile", {
    method: "GET",
  });
}

export async function updateProfile(data: UserProfileUpdate): Promise<UserProfileResponse> {
  if (shouldUseMock("profile")) {
    return {
      id: "mock_profile_id",
      user_id: "mock_user_id",
      display_name: data.display_name ?? "Maya Chen",
      headline: data.headline ?? "Product engineer",
      education_summary: data.education_summary ?? null,
      experience_summary: data.experience_summary ?? null,
      preferred_domains: data.preferred_domains ?? [],
      learning_preferences: data.learning_preferences ?? {},
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    };
  }
  return apiClient<UserProfileResponse>("/profile", {
    method: "PATCH",
    body: data,
  });
}
