import { apiClient, shouldUseMock } from "./client";
import type {
  CreateEvidenceRequest,
  EvidenceRecordResponse,
  SkillResponse,
  UserCapabilityResponse,
} from "@/types";
import { capabilities as mockCaps } from "@/lib/mocks/data";

export async function listSkills(): Promise<SkillResponse[]> {
  if (shouldUseMock("skills")) {
    return [
      { id: "sk-1", canonical_name: "React", category: "Technical" },
      { id: "sk-2", canonical_name: "TypeScript", category: "Technical" },
      { id: "sk-3", canonical_name: "Python", category: "Technical" },
      { id: "sk-4", canonical_name: "Data Structures", category: "Technical" },
      { id: "sk-5", canonical_name: "Systems Thinking", category: "Technical" },
    ];
  }
  return apiClient<SkillResponse[]>("/skills", {
    method: "GET",
  });
}

export async function listCapabilities(): Promise<UserCapabilityResponse[]> {
  if (shouldUseMock("skills")) {
    return mockCaps.map((c) => ({
      id: c.id,
      user_id: "mock_user_id",
      skill_id: c.id,
      skill_name: c.name,
      category: c.category,
      estimated_band: c.score >= 80 ? "proficient" : c.score >= 60 ? "foundational" : "claimed",
      score: c.score,
      confidence: c.score / 100,
      evidence_count: c.evidence.length,
      last_evaluated_at: new Date().toISOString(),
    }));
  }
  return apiClient<UserCapabilityResponse[]>("/capabilities", {
    method: "GET",
  });
}

export async function getCapability(skillId: string): Promise<UserCapabilityResponse> {
  if (shouldUseMock("skills")) {
    const caps = await listCapabilities();
    const found = caps.find((c) => c.skill_id === skillId || c.id === skillId);
    if (found) return found;
    return caps[0];
  }
  return apiClient<UserCapabilityResponse>(`/capabilities/${skillId}`, {
    method: "GET",
  });
}

export async function listEvidence(): Promise<EvidenceRecordResponse[]> {
  if (shouldUseMock("skills")) {
    return [
      {
        id: "ev-1",
        user_id: "mock_user_id",
        skill_id: "frontend",
        source_type: "assessment",
        summary: "React Patterns Assessment · 86%",
        confidence: 0.86,
        observed_at: new Date().toISOString(),
        created_at: new Date().toISOString(),
      },
      {
        id: "ev-2",
        user_id: "mock_user_id",
        skill_id: "frontend",
        source_type: "project",
        summary: "Kinetic UI Repository",
        confidence: 0.88,
        observed_at: new Date().toISOString(),
        created_at: new Date().toISOString(),
      },
      {
        id: "ev-3",
        user_id: "mock_user_id",
        skill_id: "systems",
        source_type: "resume",
        summary: "Resume claim: Systems thinking",
        confidence: 0.54,
        observed_at: new Date().toISOString(),
        created_at: new Date().toISOString(),
      },
    ];
  }
  return apiClient<EvidenceRecordResponse[]>("/evidence", {
    method: "GET",
  });
}

export async function addEvidence(data: CreateEvidenceRequest): Promise<EvidenceRecordResponse> {
  if (shouldUseMock("skills")) {
    return {
      id: `ev-${Date.now()}`,
      user_id: "mock_user_id",
      skill_id: "sk-mock",
      source_type: "user-confirmed",
      summary: data.summary,
      confidence: data.confidence,
      quality_metadata: { user_reported: true },
      observed_at: new Date().toISOString(),
      created_at: new Date().toISOString(),
    };
  }
  return apiClient<EvidenceRecordResponse>("/evidence", {
    method: "POST",
    body: data,
  });
}
