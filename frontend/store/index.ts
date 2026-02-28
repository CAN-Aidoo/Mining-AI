/**
 * Mining AI Platform - Zustand Store
 *
 * Slices:
 *   useUIStore   — sidebar open/close
 *   useAuthStore — JWT tokens + current user (persisted to localStorage)
 */

"use client";

import { create } from "zustand";
import { devtools, persist } from "zustand/middleware";

// ---------------------------------------------------------------------------
// UI store
// ---------------------------------------------------------------------------
interface UIState {
  sidebarOpen: boolean;
  toggleSidebar: () => void;
  setSidebarOpen: (open: boolean) => void;
}

export const useUIStore = create<UIState>()(
  devtools(
    (set) => ({
      sidebarOpen: true,
      toggleSidebar: () => set((s) => ({ sidebarOpen: !s.sidebarOpen })),
      setSidebarOpen: (open) => set({ sidebarOpen: open }),
    }),
    { name: "ui-store" }
  )
);

// ---------------------------------------------------------------------------
// Auth types
// ---------------------------------------------------------------------------
export interface AuthUser {
  id: string;
  email: string;
  full_name: string;
  is_active: boolean;
  created_at: string;
}

interface AuthState {
  user: AuthUser | null;
  accessToken: string | null;
  refreshToken: string | null;
  isAuthenticated: boolean;
  setTokens: (access: string, refresh: string) => void;
  setUser: (user: AuthUser) => void;
  logout: () => void;
}

export const useAuthStore = create<AuthState>()(
  devtools(
    persist(
      (set) => ({
        user: null,
        accessToken: null,
        refreshToken: null,
        isAuthenticated: false,
        setTokens: (access, refresh) =>
          set({ accessToken: access, refreshToken: refresh, isAuthenticated: true }),
        setUser: (user) => set({ user }),
        logout: () =>
          set({
            user: null,
            accessToken: null,
            refreshToken: null,
            isAuthenticated: false,
          }),
      }),
      {
        name: "mining-auth",
        partialize: (s) => ({
          user: s.user,
          accessToken: s.accessToken,
          refreshToken: s.refreshToken,
          isAuthenticated: s.isAuthenticated,
        }),
      }
    ),
    { name: "auth-store" }
  )
);
