import { apiClient } from "./client";

export interface HealthStatus {
  status: string;
  app_name: string;
  environment: string;
  version: string;
  database_connected: boolean;
  database_type?: string;
  gemini_configured?: boolean;
  active_questions_count?: number;
  timestamp: string;
}

export async function checkHealth(): Promise<HealthStatus> {
  return apiClient<HealthStatus>("/health");
}
