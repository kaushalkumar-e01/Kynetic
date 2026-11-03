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
