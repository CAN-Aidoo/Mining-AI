"use client";

import { useEffect, useState } from "react";
import { AppShell } from "@/components/layout/app-shell";
import { projects, research, documents, prototypes } from "@/lib/api";
import { useAuthStore } from "@/store";
import { BookOpen, FileText, FolderOpen, Zap } from "lucide-react";

interface Stats {
  projects: number;
  papers: number;
  documents: number;
  prototypes: number;
}

export default function DashboardPage() {
  const { user } = useAuthStore();
  const [stats, setStats] = useState<Stats>({ projects: 0, papers: 0, documents: 0, prototypes: 0 });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      projects.list(),
      research.list(0, 1),
      documents.list(),
      prototypes.list(),
    ])
      .then(([proj, res, docs, proto]) => {
        setStats({
          projects: proj.data.total,
          papers: res.data.total,
          documents: docs.data.total,
          prototypes: proto.data.total,
        });
      })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  const cards = [
    { label: "Projects", value: stats.projects, icon: FolderOpen, href: "/projects", color: "text-blue-500" },
    { label: "Papers", value: stats.papers, icon: BookOpen, href: "/research", color: "text-green-500" },
    { label: "Documents", value: stats.documents, icon: FileText, href: "/documents", color: "text-purple-500" },
    { label: "Prototypes", value: stats.prototypes, icon: Zap, href: "/prototypes", color: "text-orange-500" },
  ];

  return (
    <AppShell>
      <div className="p-6 max-w-5xl mx-auto">
        <div className="mb-8">
          <h1 className="text-2xl font-bold">
            Welcome back{user?.full_name ? `, ${user.full_name.split(" ")[0]}` : ""}
          </h1>
          <p className="text-muted-foreground mt-1">Here&apos;s an overview of your workspace.</p>
        </div>

        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
          {cards.map(({ label, value, icon: Icon, href, color }) => (
            <a key={label} href={href} className="bg-card border border-border rounded-xl p-5 hover:shadow-md transition-shadow">
              <div className={`mb-3 ${color}`}><Icon className="w-6 h-6" /></div>
              {loading
                ? <div className="h-8 w-12 bg-muted rounded animate-pulse mb-1" />
                : <div className="text-3xl font-bold">{value}</div>}
              <div className="text-sm text-muted-foreground mt-1">{label}</div>
            </a>
          ))}
        </div>

        <div className="bg-card border border-border rounded-xl p-6">
          <h2 className="font-semibold mb-4">Quick start</h2>
          <ol className="space-y-3 text-sm text-muted-foreground list-decimal list-inside">
            <li><a href="/projects" className="text-primary hover:underline">Create a project</a> — set your field</li>
            <li><a href="/research" className="text-primary hover:underline">Build your research library</a> — ingest papers by topic or DOI</li>
            <li><a href="/documents" className="text-primary hover:underline">Generate your document</a> — AI writes every section with real citations</li>
            <li><a href="/prototypes" className="text-primary hover:underline">Build a prototype</a> — get a working Gradio app</li>
          </ol>
        </div>
      </div>
    </AppShell>
  );
}
