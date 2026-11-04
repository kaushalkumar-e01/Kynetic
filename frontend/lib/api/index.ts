// Central Export Facade for Kynetic API Layer

export * from "./client";
export * as authApi from "./auth";
export * as profileApi from "./profile";
export * as workspaceApi from "./workspace";
export * as resumesApi from "./resumes";
export * as skillsApi from "./skills";
export * as assessmentsApi from "./assessments";
export * as projectsApi from "./projects";
export * as integrationsApi from "./integrations";
export * as goalsApi from "./goals";
export * as placementApi from "./placement";
export * as roadmapsApi from "./roadmaps";
export * as assistantApi from "./assistant";

// Legacy synchronous facades backed by mock data for backward compatibility during migration
import {
  activities,
  capabilities,
  chartData,
  currentUser,
  nextMoves,
  projects,
} from "@/lib/mocks/data";

export function getCurrentUser() {
  return currentUser;
}

export function getCapabilities() {
  return capabilities;
}

export function getRecentActivity() {
  return activities;
}

export function getProjects() {
  return projects;
}

export function getProgressSeries() {
  return chartData;
}

export function getNextMoves() {
  return nextMoves;
}
