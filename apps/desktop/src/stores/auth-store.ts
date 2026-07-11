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
  login: (email: string, name?: string) => void;
  signup: (email: string, name: string) => void;
  logout: () => void;
}

export const useAuthStore = create<AuthStore>()(
  persist(
    (set) => ({
      isAuthenticated: false,
      user: null,
      token: null,

      login: (email: string, name = "Developer") => {
        set({
          isAuthenticated: true,
          user: { email, name },
          token: "mock-jwt-token-from-cognito-auth",
        });
      },

      signup: (email: string, name: string) => {
        set({
          isAuthenticated: true,
          user: { email, name },
          token: "mock-jwt-token-from-cognito-auth",
        });
      },

      logout: () => {
        set({
          isAuthenticated: false,
          user: null,
          token: null,
        });
      },
    }),
    {
      name: "timeslice-auth",
    }
  )
);
