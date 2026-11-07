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

export function getApiBaseUrl(): string {
  let raw = process.env.NEXT_PUBLIC_API_BASE_URL?.trim();

  if (!raw) {
    if (typeof window !== "undefined" && window.location.hostname) {
      // Automatically match the browser's current hostname (localhost, 127.0.0.1, or LAN IP)
      const host = window.location.hostname;
      raw = `http://${host}:8000/api/v1`;
    } else {
      raw = "http://localhost:8000/api/v1";
    }
  }

  // Remove trailing slashes
  raw = raw.replace(/\/+$/, "");

  // Guarantee /api/v1 prefix exists so requests don't hit 404 if user omitted it
  if (!raw.endsWith("/api/v1")) {
    raw = `${raw}/api/v1`;
  }

  return raw;
}

export interface RequestOptions extends Omit<RequestInit, "body"> {
  body?: unknown;
  params?: Record<string, string | number | boolean | undefined>;
}

export async function apiClient<T>(endpoint: string, options: RequestOptions = {}): Promise<T> {
  const { body, params, headers = {}, ...rest } = options;

  const base = getApiBaseUrl();
  let url = endpoint.startsWith("http")
    ? endpoint
    : `${base}${endpoint.startsWith("/") ? endpoint : `/${endpoint}`}`;

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

  // Seamless cross-origin & cross-port token attachment (localhost:3000 -> localhost:8000)
  if (typeof window !== "undefined") {
    try {
      const storedToken = localStorage.getItem("kynetic_access_token");
      if (storedToken && !finalHeaders.has("Authorization")) {
        finalHeaders.set("Authorization", `Bearer ${storedToken}`);
      }
    } catch {
      // LocalStorage access guarded
    }
  }

  if (body instanceof FormData) {
    finalBody = body;
    // Let browser set multipart boundary header automatically
  } else if (body !== undefined && body !== null) {
    finalHeaders.set("Content-Type", "application/json");
    finalBody = JSON.stringify(body);
  }

  let response: Response;
  try {
    response = await fetch(url, {
      ...rest,
      headers: finalHeaders,
      body: finalBody,
      credentials: "include", // Essential for HttpOnly cookie session management
    });
  } catch (netErr: unknown) {
    const rawMsg = netErr instanceof Error ? netErr.message : String(netErr);
    throw new ApiError(0, {
      code: "NETWORK_ERROR",
      message: `Unable to connect to Kynetic backend API at ${url}. Please verify that the FastAPI backend is running on port 8000. (${rawMsg})`,
      details: [{ url, originalError: rawMsg }],
    });
  }

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
      try {
        localStorage.removeItem("kynetic_access_token");
      } catch {
        // Ignored
      }
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

