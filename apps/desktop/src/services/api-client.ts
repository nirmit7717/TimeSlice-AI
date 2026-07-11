import axios from "axios";

/**
 * Shared Axios client for all TimeSlice AI API calls.
 * Base URL points to the FastAPI backend.
 */
export const apiClient = axios.create({
  baseURL: "http://localhost:8000/api/v1",
  headers: {
    "Content-Type": "application/json",
  },
  timeout: 10_000,
});

// ── Response Interceptor: normalize error messages ───────────────────────────
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    const message =
      error?.response?.data?.detail ??
      error?.message ??
      "An unknown error occurred";
    console.error("[API Error]", message);
    return Promise.reject(new Error(message));
  }
);
