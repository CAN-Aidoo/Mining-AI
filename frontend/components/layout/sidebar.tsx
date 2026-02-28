"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import {
  BookOpen,
  ChevronLeft,
  ChevronRight,
  FileText,
  FolderOpen,
  LayoutDashboard,
  LogOut,
  Zap,
} from "lucide-react";

import { auth } from "@/lib/api";
import { useAuthStore, useUIStore } from "@/store";

const NAV = [
  { href: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { href: "/projects", label: "Projects", icon: FolderOpen },
  { href: "/research", label: "Research", icon: BookOpen },
  { href: "/documents", label: "Documents", icon: FileText },
  { href: "/prototypes", label: "Prototypes", icon: Zap },
];

export function Sidebar() {
  const pathname = usePathname();
  const router = useRouter();
  const { sidebarOpen, toggleSidebar } = useUIStore();
  const { user, logout } = useAuthStore();

  const handleLogout = async () => {
    try {
      await auth.logout();
    } catch {}
    logout();
    router.push("/login");
  };

  return (
    <aside
      className={`
        flex flex-col h-screen bg-card border-r border-border
        transition-all duration-200 shrink-0
        ${sidebarOpen ? "w-56" : "w-14"}
      `}
    >
      {/* Header */}
      <div className="flex items-center justify-between p-3 border-b border-border">
        {sidebarOpen && (
          <span className="font-bold text-sm text-foreground">Mining AI</span>
        )}
        <button
          onClick={toggleSidebar}
          className="p-1 rounded hover:bg-muted transition-colors ml-auto"
          aria-label="Toggle sidebar"
        >
          {sidebarOpen ? (
            <ChevronLeft className="w-4 h-4" />
          ) : (
            <ChevronRight className="w-4 h-4" />
          )}
        </button>
      </div>

      {/* Nav */}
      <nav className="flex-1 py-2 overflow-y-auto">
        {NAV.map(({ href, label, icon: Icon }) => {
          const active = pathname.startsWith(href);
          return (
            <Link
              key={href}
              href={href}
              className={`
                flex items-center gap-3 px-3 py-2 mx-1 rounded-md text-sm
                transition-colors
                ${active
                  ? "bg-primary text-primary-foreground font-medium"
                  : "text-muted-foreground hover:bg-muted hover:text-foreground"
                }
              `}
            >
              <Icon className="w-4 h-4 shrink-0" />
              {sidebarOpen && <span>{label}</span>}
            </Link>
          );
        })}
      </nav>

      {/* Footer */}
      <div className="border-t border-border p-2">
        {sidebarOpen && user && (
          <div className="px-2 py-1 mb-1">
            <p className="text-xs font-medium truncate">{user.full_name}</p>
            <p className="text-xs text-muted-foreground truncate">{user.email}</p>
          </div>
        )}
        <button
          onClick={handleLogout}
          className="flex items-center gap-3 w-full px-2 py-2 rounded-md text-sm text-muted-foreground hover:bg-muted hover:text-foreground transition-colors"
        >
          <LogOut className="w-4 h-4 shrink-0" />
          {sidebarOpen && <span>Sign out</span>}
        </button>
      </div>
    </aside>
  );
}
