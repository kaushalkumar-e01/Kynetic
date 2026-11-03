import type { ApiErrorDetail, ApiErrorEnvelope } from "@/types";

export class ApiError extends Error {
  code: string;
  details: unknown[];
  status: number;

  constructor(status: number, errorDetail: ApiErrorDetail) {
    super(errorDetail.message || "An unexpected API error occurred.");
    this.name = "ApiError";
    this.status = status;
    this.code = errorDetail.code || "UNKNOWN_ERROR";
    this.details = Array.isArray(errorDetail.details) ? errorDetail.details : [];
  }
}

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL?.replace(/\/+$/, "") || "http://localhost:8000/api/v1";

export interface RequestOptions extends Omit<RequestInit, "body"> {
  body?: unknown;
  params?: Record<string, string | number | boolean | undefined>;
}

export async function apiClient<T>(endpoint: string, options: RequestOptions = {}): Promise<T> {
  const { body, params, headers = {}, ...rest } = options;

  let url = endpoint.startsWith("http")
    ? endpoint
    : `${API_BASE_URL}${endpoint.startsWith("/") ? endpoint : `/${endpoint}`}`;

  if (params) {
    const searchParams = new URLSearchParams();
    for (const [key, val] of Object.entries(params)) {
      if (val !== undefined && val !== null) {
        searchParams.append(key, String(val));
      }
    }
    const queryString = searchParams.toString();
    if (queryString) {
      url += (url.includes("?") ? "&" : "?") + queryString;
    }
  }

  const finalHeaders = new Headers(headers);
  let finalBody: BodyInit | undefined;

  if (body instanceof FormData) {
    finalBody = body;
    // Let browser set multipart boundary header automatically
  } else if (body !== undefined && body !== null) {
    finalHeaders.set("Content-Type", "application/json");
    finalBody = JSON.stringify(body);
  }

  const response = await fetch(url, {
    ...rest,
    headers: finalHeaders,
    body: finalBody,
    credentials: "include", // Essential for HttpOnly cookie session management
  });

  if (!response.ok) {
    let errorDetail: ApiErrorDetail = {
      code: `HTTP_${response.status}`,
      message: response.statusText || "Request failed",
      details: [],
    };

    try {
      const data = await response.json();
      if (data && typeof data === "object") {
        if ("error" in data && typeof (data as ApiErrorEnvelope).error === "object") {
          errorDetail = (data as ApiErrorEnvelope).error;
        } else if ("detail" in data) {
          errorDetail = {
            code: `HTTP_${response.status}`,
            message: typeof data.detail === "string" ? data.detail : JSON.stringify(data.detail),
            details: Array.isArray(data.detail) ? data.detail : [],
          };
        }
      }
    } catch {
      // Fallback if response is not JSON
    }

    if (response.status === 401 && typeof window !== "undefined") {
      const currentPath = window.location.pathname;
      if (currentPath !== "/login" && currentPath !== "/register" && currentPath !== "/") {
        window.location.href = `/login?redirect=${encodeURIComponent(currentPath)}`;
      }
    }

    throw new ApiError(response.status, errorDetail);
  }

  // Handle 204 No Content
  if (response.status === 204) {
    return {} as T;
  }

  const contentType = response.headers.get("content-type");
  if (contentType && contentType.includes("application/json")) {
    return (await response.json()) as T;
  }

  return (await response.text()) as unknown as T;
}

export function shouldUseMock(moduleKey?: string): boolean {
  if (process.env.NEXT_PUBLIC_USE_MOCKS === "true") {
    return true;
  }
  if (moduleKey) {
    const envVar = `NEXT_PUBLIC_MOCK_${moduleKey.toUpperCase()}`;
    if (process.env[envVar] === "true") {
      return true;
    }
  }
  return false;
}
