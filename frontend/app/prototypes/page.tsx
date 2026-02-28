"use client";

import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Plus, Trash2, Download, Zap, Loader2, Code2 } from "lucide-react";
import { AppShell } from "@/components/layout/app-shell";
import { prototypes, projects } from "@/lib/api";

const PROTOTYPE_TYPES = [
  { value: "classifier", label: "Classifier", description: "Text/data classification with sklearn" },
  { value: "recommender", label: "Recommender", description: "TF-IDF cosine similarity recommendations" },
  { value: "chatbot", label: "Chatbot", description: "Conversational AI powered by Claude" },
  { value: "text_tool", label: "Text Tool", description: "Sentiment analysis, summarisation & readability" },
  { value: "dashboard", label: "Dashboard", description: "Interactive data visualisation with Plotly" },
];

const STATUS_STYLES: Record<string, string> = {
  pending: "bg-gray-100 text-gray-700",
  building: "bg-yellow-100 text-yellow-700",
  ready: "bg-green-100 text-green-700",
  error: "bg-red-100 text-red-700",
};

const TYPE_ICONS: Record<string, string> = {
  classifier: "🏷️",
  recommender: "🎯",
  chatbot: "💬",
  text_tool: "✍️",
  dashboard: "📊",
};

export default function PrototypesPage() {
  const qc = useQueryClient();

  // Create form state
  const [showForm, setShowForm] = useState(false);
  const [formTitle, setFormTitle] = useState("");
  const [protoType, setProtoType] = useState("classifier");
  const [description, setDescription] = useState("");
  const [inputDescription, setInputDescription] = useState("");
  const [projectId, setProjectId] = useState("");
  const [formError, setFormError] = useState("");

  // ── Queries ──────────────────────────────────────────────────────────────
  const { data: protoList, isLoading } = useQuery({
    queryKey: ["prototypes"],
    queryFn: () => prototypes.list().then((r) => r.data),
    refetchInterval: (query) => {
      const items: any[] = query.state.data?.items ?? [];
      return items.some((p) => p.status === "building") ? 4000 : false;
    },
  });

  const { data: projectList } = useQuery({
    queryKey: ["projects"],
    queryFn: () => projects.list().then((r) => r.data),
  });

  // ── Mutations ────────────────────────────────────────────────────────────
  const createMut = useMutation({
    mutationFn: () =>
      prototypes.create({
        title: formTitle,
        prototype_type: protoType,
        description,
        input_description: inputDescription,
        project_id: projectId,
      }),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["prototypes"] });
      setShowForm(false);
      setFormTitle(""); setProtoType("classifier");
      setDescription(""); setInputDescription(""); setProjectId("");
    },
    onError: (err: any) =>
      setFormError(err?.response?.data?.detail || "Failed to create prototype"),
  });

  const buildMut = useMutation({
    mutationFn: (id: string) => prototypes.build(id),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["prototypes"] }),
  });

  const deleteMut = useMutation({
    mutationFn: (id: string) => prototypes.remove(id),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["prototypes"] }),
  });

  const handleCreate = (e: React.FormEvent) => {
    e.preventDefault();
    setFormError("");
    if (!formTitle.trim()) { setFormError("Title is required"); return; }
    if (!description.trim()) { setFormError("Description is required"); return; }
    if (!inputDescription.trim()) { setFormError("Input description is required"); return; }
    if (!projectId) { setFormError("Please select a project"); return; }
    createMut.mutate();
  };

  return (
    <AppShell>
      <div className="p-6 max-w-5xl mx-auto">
        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="text-2xl font-bold">Prototype Builder</h1>
            <p className="text-muted-foreground text-sm mt-1">
              Generate working Gradio demos from your project description
            </p>
          </div>
          <button
            onClick={() => setShowForm(!showForm)}
            className="flex items-center gap-2 px-4 py-2 rounded-lg bg-primary text-primary-foreground text-sm font-medium hover:opacity-90"
          >
            <Plus className="w-4 h-4" /> New prototype
          </button>
        </div>

        {/* Create form */}
        {showForm && (
          <div className="bg-card border border-border rounded-xl p-5 mb-6">
            <h2 className="font-semibold mb-4">Create prototype</h2>
            {formError && (
              <div className="mb-3 px-3 py-2 rounded bg-destructive/10 text-destructive text-sm">{formError}</div>
            )}
            <form onSubmit={handleCreate} className="space-y-4">
              <input
                className="w-full px-3 py-2 rounded-lg border border-input bg-background text-sm focus:outline-none focus:ring-2 focus:ring-ring"
                placeholder="Prototype title"
                value={formTitle}
                onChange={(e) => setFormTitle(e.target.value)}
              />

              {/* Type selector */}
              <div>
                <p className="text-sm font-medium mb-2">Prototype type</p>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                  {PROTOTYPE_TYPES.map((t) => (
                    <label
                      key={t.value}
                      className={`flex items-start gap-3 p-3 rounded-lg border cursor-pointer transition-colors ${
                        protoType === t.value
                          ? "border-primary bg-primary/5"
                          : "border-border hover:bg-muted/50"
                      }`}
                    >
                      <input
                        type="radio"
                        name="type"
                        value={t.value}
                        checked={protoType === t.value}
                        onChange={() => setProtoType(t.value)}
                        className="mt-0.5"
                      />
                      <div>
                        <p className="text-sm font-medium">
                          {TYPE_ICONS[t.value]} {t.label}
                        </p>
                        <p className="text-xs text-muted-foreground">{t.description}</p>
                      </div>
                    </label>
                  ))}
                </div>
              </div>

              <textarea
                className="w-full px-3 py-2 rounded-lg border border-input bg-background text-sm focus:outline-none focus:ring-2 focus:ring-ring resize-none"
                placeholder="Project description — what does it do? What problem does it solve?"
                rows={3}
                value={description}
                onChange={(e) => setDescription(e.target.value)}
              />

              <textarea
                className="w-full px-3 py-2 rounded-lg border border-input bg-background text-sm focus:outline-none focus:ring-2 focus:ring-ring resize-none"
                placeholder="Input description — what data will users provide? e.g. 'CSV file with student grades'"
                rows={2}
                value={inputDescription}
                onChange={(e) => setInputDescription(e.target.value)}
              />

              <select
                className="w-full px-3 py-2 rounded-lg border border-input bg-background text-sm focus:outline-none focus:ring-2 focus:ring-ring"
                value={projectId}
                onChange={(e) => setProjectId(e.target.value)}
              >
                <option value="">Select a project…</option>
                {projectList?.items?.map((p: any) => (
                  <option key={p.id} value={p.id}>{p.title}</option>
                ))}
              </select>

              <div className="flex gap-2">
                <button
                  type="submit"
                  disabled={createMut.isPending}
                  className="px-4 py-2 rounded-lg bg-primary text-primary-foreground text-sm font-medium hover:opacity-90 disabled:opacity-60"
                >
                  {createMut.isPending ? "Creating…" : "Create"}
                </button>
                <button
                  type="button"
                  onClick={() => setShowForm(false)}
                  className="px-4 py-2 rounded-lg border border-border text-sm hover:bg-muted"
                >
                  Cancel
                </button>
              </div>
            </form>
          </div>
        )}

        {/* Prototype list */}
        {isLoading ? (
          <div className="space-y-3">
            {[1, 2, 3].map((i) => (
              <div key={i} className="h-24 bg-muted rounded-xl animate-pulse" />
            ))}
          </div>
        ) : protoList?.items?.length === 0 ? (
          <div className="text-center py-20 text-muted-foreground">
            <Code2 className="w-10 h-10 mx-auto mb-3 opacity-30" />
            <p className="font-medium">No prototypes yet</p>
            <p className="text-sm mt-1">Create a prototype to generate a working Gradio app.</p>
          </div>
        ) : (
          <div className="space-y-3">
            {protoList?.items?.map((proto: any) => (
              <div
                key={proto.id}
                className="bg-card border border-border rounded-xl p-5"
              >
                <div className="flex items-start justify-between gap-4">
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1">
                      <span className="text-lg">{TYPE_ICONS[proto.prototype_type] ?? "🤖"}</span>
                      <h3 className="font-medium">{proto.title}</h3>
                      <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${STATUS_STYLES[proto.status] ?? "bg-muted text-muted-foreground"}`}>
                        {proto.status}
                        {proto.status === "building" && (
                          <Loader2 className="w-3 h-3 inline ml-1 animate-spin" />
                        )}
                      </span>
                    </div>
                    <p className="text-sm text-muted-foreground capitalize">
                      {proto.prototype_type.replace("_", " ")} ·{" "}
                      {new Date(proto.created_at).toLocaleDateString()}
                    </p>
                    {proto.description && (
                      <p className="text-sm text-muted-foreground mt-1 line-clamp-2">
                        {proto.description}
                      </p>
                    )}
                    {proto.status === "error" && proto.build_log && (
                      <p className="text-xs text-destructive mt-2 font-mono line-clamp-2">
                        {proto.build_log}
                      </p>
                    )}
                  </div>

                  <div className="flex items-center gap-2 shrink-0">
                    {proto.status !== "building" && (
                      <button
                        onClick={() => buildMut.mutate(proto.id)}
                        disabled={buildMut.isPending}
                        className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-primary text-primary-foreground text-xs font-medium hover:opacity-90 disabled:opacity-60"
                      >
                        <Zap className="w-3.5 h-3.5" />
                        {proto.status === "ready" ? "Rebuild" : "Build"}
                      </button>
                    )}
                    {proto.status === "ready" && (
                      <a
                        href={prototypes.downloadUrl(proto.id)}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-border text-xs font-medium hover:bg-muted"
                      >
                        <Download className="w-3.5 h-3.5" /> Download ZIP
                      </a>
                    )}
                    <button
                      onClick={() => deleteMut.mutate(proto.id)}
                      disabled={deleteMut.isPending}
                      className="p-1.5 rounded hover:bg-muted text-muted-foreground hover:text-destructive"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </AppShell>
  );
}
