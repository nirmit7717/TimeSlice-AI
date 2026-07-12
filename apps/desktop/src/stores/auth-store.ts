import { create } from "zustand";
import { persist } from "zustand/middleware";

interface User {
  email: string;
  name: string;
}

interface AuthStore {
  isAuthenticated: boolean;
  user: User | null;
  token: string | null;
  error: string | null;
  login: (email: string, password?: string) => Promise<void>;
  signup: (email: string, name: string, password?: string) => Promise<void>;
  logout: () => Promise<void>;
}

const API_BASE = "http://127.0.0.1:8000/api/v1/auth";

export const useAuthStore = create<AuthStore>()(
  persist(
    (set) => ({
      isAuthenticated: false,
      user: null,
      token: null,
      error: null,

      login: async (email, password = "defaultpassword") => {
        set({ error: null });
        try {
          const params = new URLSearchParams();
          params.append("username", email); // FastAPI OAuth2PasswordRequestForm expects username
          params.append("password", password);

          const res = await fetch(`${API_BASE}/login`, {
            method: "POST",
            headers: {
              "Content-Type": "application/x-www-form-urlencoded",
            },
            body: params,
          });

          if (!res.ok) {
            const errData = await res.json();
            throw new Error(errData.detail || "Authentication failed");
          }

          const data = await res.json();
          set({
            isAuthenticated: true,
            token: data.access_token,
            user: { email: data.user_email, name: data.user_name },
          });
        } catch (err) {
          set({ error: String(err) });
          throw err;
        }
      },

      signup: async (email, name, password = "defaultpassword") => {
        set({ error: null });
        try {
          const res = await fetch(`${API_BASE}/register`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ email, password, name }),
          });

          if (!res.ok) {
            const errData = await res.json();
            throw new Error(errData.detail || "Registration failed");
          }

          const data = await res.json();
          set({
            isAuthenticated: true,
            token: data.access_token,
            user: { email: data.user_email, name: data.user_name },
          });
        } catch (err) {
          set({ error: String(err) });
          throw err;
        }
      },

      logout: async () => {
        try {
          await fetch(`${API_BASE}/logout`, { method: "POST" });
        } catch (err) {
          console.error("Logout request failed:", err);
        }
        set({
          isAuthenticated: false,
          user: null,
          token: null,
          error: null,
        });
      },
    }),
    {
      name: "timeslice-auth",
    }
  )
);
