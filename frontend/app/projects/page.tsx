"use client";

import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Plus, Trash2 } from "lucide-react";
import { AppShell } from "@/components/layout/app-shell";
import { projects } from "@/lib/api";

const FIELDS = [
  { value: "computer_science", label: "Computer Science" },
  { value: "engineering", label: "Engineering" },
  { value: "business", label: "Business" },
  { value: "health_sciences", label: "Health Sciences" },
];

const STATUS_COLORS: Record<string, string> = {
  draft: "bg-gray-100 text-gray-700",
  in_progress: "bg-blue-100 text-blue-700",
  completed: "bg-green-100 text-green-700",
};

export default function ProjectsPage() {
  const qc = useQueryClient();
  const [showForm, setShowForm] = useState(false);
  const [title, setTitle] = useState("");
  const [field, setField] = useState("computer_science");
  const [description, setDescription] = useState("");
  const [formError, setFormError] = useState("");

  const { data, isLoading } = useQuery({
    queryKey: ["projects"],
    queryFn: () => projects.list().then((r) => r.data),
  });

  const createMut = useMutation({
    mutationFn: () => projects.create({ title, field, description: description || undefined }),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["projects"] });
      setShowForm(false);
      setTitle(""); setField("computer_science"); setDescription("");
    },
    onError: (err: any) => setFormError(err?.response?.data?.detail || "Failed to create project"),
  });

  const deleteMut = useMutation({
    mutationFn: (id: string) => projects.remove(id),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["projects"] }),
  });

  const handleCreate = (e: React.FormEvent) => {
    e.preventDefault();
    setFormError("");
    if (!title.trim()) { setFormError("Title is required"); return; }
    createMut.mutate();
  };

  return (
    <AppShell>
      <div className="p-6 max-w-4xl mx-auto">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="text-2xl font-bold">Projects</h1>
            <p className="text-muted-foreground text-sm mt-1">Manage your final year projects</p>
          </div>
          <button
            onClick={() => setShowForm(!showForm)}
            className="flex items-center gap-2 px-4 py-2 rounded-lg bg-primary text-primary-foreground text-sm font-medium hover:opacity-90"
          >
            <Plus className="w-4 h-4" /> New project
          </button>
        </div>

        {showForm && (
          <div className="bg-card border border-border rounded-xl p-5 mb-6">
            <h2 className="font-semibold mb-4">Create project</h2>
            {formError && (
              <div className="mb-3 px-3 py-2 rounded bg-destructive/10 text-destructive text-sm">{formError}</div>
            )}
            <form onSubmit={handleCreate} className="space-y-3">
              <input
                className="w-full px-3 py-2 rounded-lg border border-input bg-background text-sm focus:outline-none focus:ring-2 focus:ring-ring"
                placeholder="Project title"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
              />
              <select
                className="w-full px-3 py-2 rounded-lg border border-input bg-background text-sm focus:outline-none focus:ring-2 focus:ring-ring"
                value={field}
                onChange={(e) => setField(e.target.value)}
              >
                {FIELDS.map((f) => <option key={f.value} value={f.value}>{f.label}</option>)}
              </select>
              <textarea
                className="w-full px-3 py-2 rounded-lg border border-input bg-background text-sm focus:outline-none focus:ring-2 focus:ring-ring resize-none"
                placeholder="Description (optional)"
                rows={2}
                value={description}
                onChange={(e) => setDescription(e.target.value)}
              />
              <div className="flex gap-2">
                <button type="submit" disabled={createMut.isPending} className="px-4 py-2 rounded-lg bg-primary text-primary-foreground text-sm font-medium hover:opacity-90 disabled:opacity-60">
                  {createMut.isPending ? "Creating…" : "Create"}
                </button>
                <button type="button" onClick={() => setShowForm(false)} className="px-4 py-2 rounded-lg border border-border text-sm hover:bg-muted">
                  Cancel
                </button>
              </div>
            </form>
          </div>
        )}

        {isLoading ? (
          <div className="space-y-3">
            {[1, 2, 3].map((i) => (
              <div key={i} className="h-20 bg-muted rounded-xl animate-pulse" />
            ))}
          </div>
        ) : data?.items.length === 0 ? (
          <div className="text-center py-20 text-muted-foreground">
            <p className="text-lg font-medium">No projects yet</p>
            <p className="text-sm mt-1">Create your first project to get started.</p>
          </div>
        ) : (
          <div className="space-y-3">
            {data?.items.map((project: any) => (
              <div key={project.id} className="bg-card border border-border rounded-xl p-4 flex items-center justify-between hover:shadow-sm transition-shadow">
                <div>
                  <div className="flex items-center gap-2 mb-1">
                    <h3 className="font-medium">{project.title}</h3>
                    <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${STATUS_COLORS[project.status] || "bg-muted text-muted-foreground"}`}>
                      {project.status.replace("_", " ")}
                    </span>
                  </div>
                  <p className="text-sm text-muted-foreground">
                    {project.field.replace("_", " ")} · Created {new Date(project.created_at).toLocaleDateString()}
                  </p>
                  {project.description && (
                    <p className="text-sm text-muted-foreground mt-1 line-clamp-1">{project.description}</p>
                  )}
                </div>
                <button
                  onClick={() => deleteMut.mutate(project.id)}
                  disabled={deleteMut.isPending}
                  className="p-2 rounded-lg text-muted-foreground hover:bg-muted hover:text-destructive transition-colors"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
            ))}
          </div>
        )}
      </div>
    </AppShell>
  );
}
