import { CuratedRoadmap, RoadmapPhase, RoadmapProgressData, UserProgressStore } from "@/data/roadmaps";

const STORAGE_PREFIX = "kynetic_roadmap_progress_v1_";

export function getStorageKey(userId?: string | null): string {
  const safeId = (userId && userId.trim()) || "guest_user";
  return `${STORAGE_PREFIX}${safeId}`;
}

export function loadUserProgress(userId?: string | null): UserProgressStore {
  if (typeof window === "undefined") return {};
  try {
    const raw = localStorage.getItem(getStorageKey(userId));
    if (!raw) return {};
    const parsed = JSON.parse(raw);
    return typeof parsed === "object" && parsed !== null ? parsed : {};
  } catch (err) {
    console.error("Failed to load user roadmap progress from localStorage", err);
    return {};
  }
}

export function saveUserProgress(userId: string | null | undefined, store: UserProgressStore): void {
  if (typeof window === "undefined") return;
  try {
    localStorage.setItem(getStorageKey(userId), JSON.stringify(store));
  } catch (err) {
    console.error("Failed to save user roadmap progress to localStorage", err);
  }
}

export function toggleTopicCompletion(
  userId: string | null | undefined,
  roadmapId: string,
  topicId: string
): { updatedStore: UserProgressStore; isCompleted: boolean } {
  const store = loadUserProgress(userId);
  const roadmapProgress: RoadmapProgressData = { ...(store[roadmapId] || {}) };
  const current = roadmapProgress[topicId]?.completed || false;
  const nextCompleted = !current;

  roadmapProgress[topicId] = {
    completed: nextCompleted,
    completedAt: nextCompleted ? new Date().toISOString() : undefined,
  };

  const updatedStore: UserProgressStore = {
    ...store,
    [roadmapId]: roadmapProgress,
  };

  saveUserProgress(userId, updatedStore);
  return { updatedStore, isCompleted: nextCompleted };
}

export interface PhaseProgressStats {
  phaseId: string;
  totalTopics: number;
  completedTopics: number;
  percentage: number;
}

export interface RoadmapProgressStats {
  totalTopics: number;
  completedTopics: number;
  percentage: number;
  isStarted: boolean;
  isCompleted: boolean;
  phases: Record<string, PhaseProgressStats>;
}

export function calculateRoadmapProgress(
  roadmap: CuratedRoadmap,
  progressData?: RoadmapProgressData
): RoadmapProgressStats {
  const data = progressData || {};
  let totalTopics = 0;
  let completedTopics = 0;
  const phaseStats: Record<string, PhaseProgressStats> = {};

  roadmap.phases.forEach((phase) => {
    let pTotal = 0;
    let pCompleted = 0;

    phase.topics.forEach((t) => {
      pTotal += 1;
      totalTopics += 1;
      if (data[t.id]?.completed) {
        pCompleted += 1;
        completedTopics += 1;
      }
    });

    phaseStats[phase.id] = {
      phaseId: phase.id,
      totalTopics: pTotal,
      completedTopics: pCompleted,
      percentage: pTotal > 0 ? Math.round((pCompleted / pTotal) * 100) : 0,
    };
  });

  const percentage = totalTopics > 0 ? Math.round((completedTopics / totalTopics) * 100) : 0;

  return {
    totalTopics,
    completedTopics,
    percentage,
    isStarted: completedTopics > 0,
    isCompleted: totalTopics > 0 && completedTopics === totalTopics,
    phases: phaseStats,
  };
}

