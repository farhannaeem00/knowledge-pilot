/**
 * Zustand store for auth state, persisted to localStorage. Holds the
 * current user object (not tokens - those live separately in
 * api-client.ts's own localStorage keys, managed independently since
 * they're refreshed outside of any component lifecycle).
 */
import { create } from "zustand";
import { persist } from "zustand/middleware";
import type { User } from "@/types/api";

interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  setUser: (user: User | null) => void;
  logout: () => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      user: null,
      isAuthenticated: false,
      setUser: (user) => set({ user, isAuthenticated: !!user }),
      logout: () => set({ user: null, isAuthenticated: false }),
    }),
    { name: "kp-auth-storage" }
  )
);