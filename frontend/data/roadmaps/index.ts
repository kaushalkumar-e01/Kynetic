import { CuratedRoadmap, RoadmapCategory, RoadmapDifficulty } from "./types";
import { cRoadmap } from "./c-roadmap";
import { cppRoadmap } from "./cpp-roadmap";
import { pythonRoadmap } from "./python-roadmap";
import { dsaRoadmap } from "./dsa-roadmap";
import { mysqlRoadmap } from "./mysql-roadmap";
import { fullstackRoadmap } from "./fullstack-roadmap";

export * from "./types";
export { cRoadmap, cppRoadmap, pythonRoadmap, dsaRoadmap, mysqlRoadmap, fullstackRoadmap };

export const ALL_CURATED_ROADMAPS: CuratedRoadmap[] = [
  cRoadmap,
  cppRoadmap,
  pythonRoadmap,
  dsaRoadmap,
  mysqlRoadmap,
  fullstackRoadmap,
];

export function getCuratedRoadmapById(id: string): CuratedRoadmap | undefined {
  return ALL_CURATED_ROADMAPS.find((r) => r.id === id || r.slug === id);
}

export function getTotalTopicCount(roadmap: CuratedRoadmap): number {
  return roadmap.phases.reduce((acc, phase) => acc + phase.topics.length, 0);
}

export function filterCuratedRoadmaps(
  roadmaps: CuratedRoadmap[],
  searchQuery: string,
  categoryFilter: string,
  difficultyFilter: string
): CuratedRoadmap[] {
  const query = searchQuery.trim().toLowerCase();

  return roadmaps.filter((rm) => {
    // Category match
    if (categoryFilter !== "all" && rm.category.toLowerCase() !== categoryFilter.toLowerCase()) {
      return false;
    }

    // Difficulty match
    if (difficultyFilter !== "all" && rm.difficulty.toLowerCase() !== difficultyFilter.toLowerCase()) {
      return false;
    }

    // Search query match (title, tagline, description, topics)
    if (query) {
      const titleMatch = rm.title.toLowerCase().includes(query);
      const taglineMatch = rm.tagline.toLowerCase().includes(query);
      const descMatch = rm.description.toLowerCase().includes(query);
      const topicMatch = rm.phases.some((phase) =>
        phase.topics.some(
          (t) =>
            t.title.toLowerCase().includes(query) ||
            t.shortDescription.toLowerCase().includes(query) ||
            t.learningObjectives.some((obj) => obj.toLowerCase().includes(query))
        )
      );

      return titleMatch || taglineMatch || descMatch || topicMatch;
    }

    return true;
  });
}

