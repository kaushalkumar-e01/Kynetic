export type ResourceType = "documentation" | "tutorial" | "article" | "interactive" | "video";

export interface LearningResource {
  title: string;
  url: string;
  publisher: string;
  type: ResourceType;
  isFree: true;
}

export interface RoadmapTopic {
  id: string;
  title: string;
  shortDescription: string;
  learningObjectives: string[];
  prerequisites?: string[];
  isEssential: boolean;
  resources: LearningResource[];
}

export interface RoadmapPhase {
  id: string;
  order: number;
  title: string;
  description: string;
  topics: RoadmapTopic[];
}

export type RoadmapCategory = "Languages" | "Computer Science" | "Databases" | "Web Development";
export type RoadmapDifficulty = "Beginner" | "Intermediate" | "Advanced";

export interface CuratedRoadmap {
  id: string;
  slug: string;
  title: string;
  tagline: string;
  description: string;
  category: RoadmapCategory;
  difficulty: RoadmapDifficulty;
  estimatedDuration: string;
  badgeColor?: string;
  phases: RoadmapPhase[];
}

export interface TopicProgress {
  completed: boolean;
  completedAt?: string;
}

export interface RoadmapProgressData {
  [topicId: string]: TopicProgress;
}

export interface UserProgressStore {
  [roadmapId: string]: RoadmapProgressData;
}

