import { vi, beforeEach, describe, it, expect } from "vitest";

// Mock localStorage globally
const localStorageMock = (() => {
  let store: Record<string, string> = {};
  return {
    getItem: (key: string) => store[key] || null,
    setItem: (key: string, value: string) => { store[key] = value.toString(); },
    clear: () => { store = {}; },
    removeItem: (key: string) => { delete store[key]; }
  };
})();
Object.defineProperty(global, "localStorage", { value: localStorageMock });

import { useAuthStore } from "../stores/auth-store";

describe("auth-store", () => {
  beforeEach(() => {
    localStorage.clear();
    useAuthStore.setState({
      isAuthenticated: false,
      user: null,
      token: null,
      error: null,
    });
    vi.restoreAllMocks();
  });

  it("should have initial unauthenticated state", () => {
    const state = useAuthStore.getState();
    expect(state.isAuthenticated).toBe(false);
    expect(state.user).toBeNull();
    expect(state.token).toBeNull();
  });

  it("should log in successfully", async () => {
    const mockLoginResponse = {
      access_token: "mock-jwt-token",
      user_email: "test@example.com",
      user_name: "Test User",
    };

    const fetchMock = vi.fn().mockImplementation(() =>
      Promise.resolve({
        ok: true,
        json: () => Promise.resolve(mockLoginResponse),
      })
    );
    global.fetch = fetchMock;

    await useAuthStore.getState().login("test@example.com", "password123");

    const state = useAuthStore.getState();
    expect(state.isAuthenticated).toBe(true);
    expect(state.token).toBe("mock-jwt-token");
    expect(state.user).toEqual({
      email: "test@example.com",
      name: "Test User",
    });
  });

  it("should set error state on login failure", async () => {
    const mockErrorResponse = {
      detail: "Invalid credentials",
    };

    const fetchMock = vi.fn().mockImplementation(() =>
      Promise.resolve({
        ok: false,
        json: () => Promise.resolve(mockErrorResponse),
      })
    );
    global.fetch = fetchMock;

    await expect(
      useAuthStore.getState().login("test@example.com", "wrong")
    ).rejects.toThrow("Invalid credentials");

    const state = useAuthStore.getState();
    expect(state.isAuthenticated).toBe(false);
    expect(state.error).toContain("Invalid credentials");
  });
});
