import { apiClient, shouldUseMock } from "./client";
import type { TokenResponse, UserLoginRequest, UserRegisterRequest, UserResponse } from "@/types";
import { currentUser as mockUser } from "@/lib/mocks/data";

export async function register(data: UserRegisterRequest): Promise<TokenResponse> {
  if (shouldUseMock("auth")) {
    return {
      access_token: "mock_jwt_token",
      token_type: "bearer",
      user: {
        id: "mock_user_id",
        email: data.email,
        account_status: "active",
        created_at: new Date().toISOString(),
      },
    };
  }
  const res = await apiClient<TokenResponse>("/auth/register", {
    method: "POST",
    body: data,
  });
  if (res?.access_token && typeof window !== "undefined") {
    try {
      localStorage.setItem("kynetic_access_token", res.access_token);
    } catch {
      // Storage access guarded
    }
  }
  return res;
}

export async function login(data: UserLoginRequest): Promise<TokenResponse> {
  if (shouldUseMock("auth")) {
    return {
      access_token: "mock_jwt_token",
      token_type: "bearer",
      user: {
        id: "mock_user_id",
        email: data.email,
        account_status: "active",
        created_at: new Date().toISOString(),
      },
    };
  }
  const res = await apiClient<TokenResponse>("/auth/login", {
    method: "POST",
    body: data,
  });
  if (res?.access_token && typeof window !== "undefined") {
    try {
      localStorage.setItem("kynetic_access_token", res.access_token);
    } catch {
      // Storage access guarded
    }
  }
  return res;
}

export async function logout(): Promise<{ message: string }> {
  if (typeof window !== "undefined") {
    try {
      localStorage.removeItem("kynetic_access_token");
    } catch {
      // Storage access guarded
    }
  }
  if (shouldUseMock("auth")) {
    return { message: "Logged out successfully (mock)." };
  }
  return apiClient<{ message: string }>("/auth/logout", {
    method: "POST",
  });
}

export async function getMe(): Promise<UserResponse> {
  if (shouldUseMock("auth")) {
    return {
      id: "mock_user_id",
      email: "maya.chen@example.com",
      account_status: "active",
      created_at: new Date().toISOString(),
    };
  }
  return apiClient<UserResponse>("/auth/me", {
    method: "GET",
  });
}

