import { apiClient, shouldUseMock } from "./client";
import type { JobMatchCreate, JobMatchResponse } from "@/types";

export async function createJobMatch(data: JobMatchCreate): Promise<JobMatchResponse> {
  if (shouldUseMock("placement")) {
    return {
      id: `match-${Date.now()}`,
      user_id: "mock_user_id",
      goal_id: data.goal_id,
      role_title: data.role_title,
      estimated_score: 82.5,
      extracted_requirements: {
        skills: ["React", "TypeScript", "GraphQL"],
      },
      match_breakdown: {
        matched_skills: [
          { skill: "React", required_level: "proficient", user_score: 86.0, status: "strong" },
          { skill: "TypeScript", required_level: "proficient", user_score: 80.0, status: "strong" },
        ],
        missing_skills: [
          { skill: "GraphQL", required_level: "foundational", user_score: 0.0, status: "gap" },
        ],
      },
      limitations: [
        "Strengthen GraphQL knowledge through project implementation or tutorial.",
        "Add unit test evidence for React components.",
      ],
      created_at: new Date().toISOString(),
    };
  }
  return apiClient<JobMatchResponse>("/placement/matches", {
    method: "POST",
    body: data,
  });
}

export async function listJobMatches(): Promise<JobMatchResponse[]> {
  if (shouldUseMock("placement")) {
    return [
      {
        id: "match-1",
        user_id: "mock_user_id",
        role_title: "Frontend Software Engineer (Early Career)",
        estimated_score: 84.0,
        extracted_requirements: {
          skills: ["React", "TypeScript", "Tailwind CSS"],
        },
        match_breakdown: {
          matched: ["React", "TypeScript", "Tailwind CSS"],
          gaps: ["GraphQL", "Next.js SSR"],
        },
        limitations: [
          "Demonstrate Next.js SSR in your portfolio project.",
          "React capability is in the proficient band with 86% assessed score.",
        ],
        created_at: new Date().toISOString(),
      },
      {
        id: "match-2",
        user_id: "mock_user_id",
        role_title: "Full Stack Engineer Intern",
        estimated_score: 72.0,
        extracted_requirements: {
          skills: ["Python", "SQL", "Git"],
        },
        match_breakdown: {
          matched: ["Python", "SQL", "Git"],
          gaps: ["Docker", "Distributed Systems"],
        },
        limitations: ["Systems thinking capability is claimed but needs assessed evidence."],
        created_at: new Date().toISOString(),
      },
    ];
  }
  return apiClient<JobMatchResponse[]>("/placement/matches", {
    method: "GET",
  });
}

export async function getJobMatch(matchId: string): Promise<JobMatchResponse> {
  if (shouldUseMock("placement")) {
    const list = await listJobMatches();
    return list.find((m) => m.id === matchId) || list[0];
  }
  return apiClient<JobMatchResponse>(`/placement/matches/${matchId}`, {
    method: "GET",
  });
}
