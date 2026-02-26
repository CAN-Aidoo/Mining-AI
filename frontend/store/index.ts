/**
 * Mining AI Platform - Zustand Store Root
 *
 * Week 1: UI state only.
 * Week 2+: Add user auth slice, project slice, generation slice, etc.
 */

import { create } from "zustand";
import { devtools } from "zustand/middleware";

interface UIState {
  sidebarOpen: boolean;
  toggleSidebar: () => void;
  setSidebarOpen: (open: boolean) => void;
}

export const useUIStore = create<UIState>()(
  devtools(
    (set) => ({
      sidebarOpen: true,
      toggleSidebar: () =>
        set((state) => ({ sidebarOpen: !state.sidebarOpen })),
      setSidebarOpen: (open: boolean) => set({ sidebarOpen: open }),
    }),
    { name: "ui-store" }
  )
);
