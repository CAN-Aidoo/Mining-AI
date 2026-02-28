"use client";

import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import {
  Plus, Trash2, FileText, Download, Zap, RefreshCw,
  ChevronDown, ChevronUp, Loader2,
} from "lucide-react";
import { AppShell } from "@/components/layout/app-shell";
import { documents, projects } from "@/lib/api";

const CITATION_STYLES = ["APA", "IEEE"] as const;

const SECTIONS_BY_FIELD: Record<string, string[]> = {
  computer_science: [
    "Abstract", "Introduction", "Literature Review", "Methodology",
    "System Design", "Implementation", "Testing & Evaluation",
    "Discussion", "Conclusion", "References",
  ],
  engineering: [
    "Abstract", "Introduction", "Literature Review", "Problem Statement",
    "Design & Methodology", "Implementation", "Results & Analysis",
    "Discussion", "Conclusion", "References",
  ],
  business: [
    "Executive Summary", "Introduction", "Literature Review", "Methodology",
    "Market Analysis", "Findings", "Discussion", "Recommendations",
    "Conclusion", "References",
  ],
  health_sciences: [
    "Abstract", "Introduction", "Literature Review", "Methodology",
    "Results", "Discussion", "Ethical Considerations", "Conclusion", "References",
  ],
};

const STATUS_STYLES: Record<string, string> = {
  draft: "bg-gray-100 text-gray-700",
  generating: "bg-yellow-100 text-yellow-700",
  ready: "bg-green-100 text-green-700",
  error: "bg-red-100 text-red-700",
};

export default function DocumentsPage() {
  const qc = useQueryClient();

  // Create form state
  const [showForm, setShowForm] = useState(false);
  const [title, setTitle] = useState("");
  const [projectId, setProjectId] = useState("");
  const [citationStyle, setCitationStyle] = useState<"APA" | "IEEE">("APA");
  const [formError, setFormError] = useState("");

  // Selection + section state
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [expandedSections, setExpandedSections] = useState<Record<string, boolean>>({});
  const [generatingSection, setGeneratingSection] = useState<string | null>(null);

  // ── Queries ──────────────────────────────────────────────────────────────
  const { data: docList, isLoading } = useQuery({
    queryKey: ["documents"],
    queryFn: () => documents.list().then((r) => r.data),
  });

  const { data: projectList } = useQuery({
    queryKey: ["projects"],
    queryFn: () => projects.list().then((r) => r.data),
  });

  const { data: activeDoc, refetch: refetchDoc } = useQuery({
    queryKey: ["document", selectedId],
    queryFn: () => documents.get(selectedId!).then((r) => r.data),
    enabled: !!selectedId,
    refetchInterval: (query) =>
      query.state.data?.status === "generating" ? 3000 : false,
  });

  // Fetch project for active doc to derive available sections
  const activeDocProjectId = activeDoc?.project_id;
  const { data: activeProject } = useQuery({
    queryKey: ["project", activeDocProjectId],
    queryFn: () => projects.get(activeDocProjectId!).then((r) => r.data),
    enabled: !!activeDocProjectId,
  });

  const availableSections =
    SECTIONS_BY_FIELD[activeProject?.field ?? "computer_science"] ?? [];

  // ── Mutations ────────────────────────────────────────────────────────────
  const createMut = useMutation({
    mutationFn: () =>
      documents.create({ title, project_id: projectId, citation_style: citationStyle }),
    onSuccess: (res) => {
      qc.invalidateQueries({ queryKey: ["documents"] });
      setSelectedId(res.data.id);
      setShowForm(false);
      setTitle(""); setProjectId(""); setCitationStyle("APA");
    },
    onError: (err: any) =>
      setFormError(err?.response?.data?.detail || "Failed to create document"),
  });

  const deleteMut = useMutation({
    mutationFn: (id: string) => documents.remove(id),
    onSuccess: (_, id) => {
      qc.invalidateQueries({ queryKey: ["documents"] });
      if (selectedId === id) setSelectedId(null);
    },
  });

  const generateAllMut = useMutation({
    mutationFn: (id: string) => documents.generateAll(id),
    onSuccess: () => setTimeout(() => refetchDoc(), 1500),
  });

  // ── Handlers ─────────────────────────────────────────────────────────────
  const handleCreate = (e: React.FormEvent) => {
    e.preventDefault();
    setFormError("");
    if (!title.trim()) { setFormError("Title is required"); return; }
    if (!projectId) { setFormError("Please select a project"); return; }
    createMut.mutate();
  };

  const handleGenerateSection = async (section: string) => {
    if (!selectedId) return;
    setGeneratingSection(section);
    try {
      await documents.generateSection(selectedId, section);
      refetchDoc();
    } catch {}
    finally { setGeneratingSection(null); }
  };

  const toggleSection = (section: string) =>
    setExpandedSections((prev) => ({ ...prev, [section]: !prev[section] }));

  const generatedContent: Record<string, string> = activeDoc?.sections ?? {};

  return (
    <AppShell>
      <div className="p-6 max-w-7xl mx-auto">
        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="text-2xl font-bold">Documents</h1>
            <p className="text-muted-foreground text-sm mt-1">
              AI-generated academic documents with real citations
            </p>
          </div>
          <button
            onClick={() => setShowForm(!showForm)}
            className="flex items-center gap-2 px-4 py-2 rounded-lg bg-primary text-primary-foreground text-sm font-medium hover:opacity-90"
          >
            <Plus className="w-4 h-4" /> New document
          </button>
        </div>

        {/* Create form */}
        {showForm && (
          <div className="bg-card border border-border rounded-xl p-5 mb-6">
            <h2 className="font-semibold mb-4">Create document</h2>
            {formError && (
              <div className="mb-3 px-3 py-2 rounded bg-destructive/10 text-destructive text-sm">{formError}</div>
            )}
            <form onSubmit={handleCreate} className="space-y-3">
              <input
                className="w-full px-3 py-2 rounded-lg border border-input bg-background text-sm focus:outline-none focus:ring-2 focus:ring-ring"
                placeholder="Document title e.g. Literature Review: Machine Learning in Healthcare"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
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
                {CITATION_STYLES.map((s) => (
                  <button
                    key={s} type="button"
                    onClick={() => setCitationStyle(s)}
                    className={`px-3 py-1 rounded-full text-xs font-medium transition-colors ${
                      citationStyle === s
                        ? "bg-primary text-primary-foreground"
                        : "bg-muted text-muted-foreground"
                    }`}
                  >
                    {s}
                  </button>
                ))}
              </div>
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

        {/* Two-column layout */}
        <div className="grid lg:grid-cols-5 gap-6">
          {/* Document list */}
          <div className="lg:col-span-2">
            {isLoading ? (
              <div className="space-y-3">
                {[1, 2, 3].map((i) => (
                  <div key={i} className="h-20 bg-muted rounded-xl animate-pulse" />
                ))}
              </div>
            ) : docList?.items?.length === 0 ? (
              <div className="text-center py-16 text-muted-foreground text-sm">
                <FileText className="w-8 h-8 mx-auto mb-2 opacity-40" />
                No documents yet. Create your first document.
              </div>
            ) : (
              <div className="space-y-2">
                {docList?.items?.map((doc: any) => (
                  <div
                    key={doc.id}
                    onClick={() => setSelectedId(doc.id)}
                    className={`cursor-pointer rounded-xl border p-4 transition-all ${
                      selectedId === doc.id
                        ? "border-primary bg-primary/5"
                        : "border-border bg-card hover:shadow-sm"
                    }`}
                  >
                    <div className="flex items-start justify-between gap-2">
                      <div className="flex-1 min-w-0">
                        <p className="font-medium text-sm leading-snug line-clamp-2">{doc.title}</p>
                        <div className="flex items-center gap-2 mt-1.5">
                          <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${STATUS_STYLES[doc.status] ?? "bg-muted text-muted-foreground"}`}>
                            {doc.status}
                          </span>
                          <span className="text-xs text-muted-foreground">{doc.citation_style}</span>
                        </div>
                        <p className="text-xs text-muted-foreground mt-1">
                          {new Date(doc.created_at).toLocaleDateString()}
                        </p>
                      </div>
                      <button
                        onClick={(e) => { e.stopPropagation(); deleteMut.mutate(doc.id); }}
                        className="p-1.5 rounded hover:bg-muted text-muted-foreground hover:text-destructive shrink-0"
                      >
                        <Trash2 className="w-3.5 h-3.5" />
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Document detail */}
          <div className="lg:col-span-3">
            {!selectedId ? (
              <div className="text-center py-20 text-muted-foreground text-sm border border-dashed border-border rounded-xl">
                Select a document to view and edit its sections
              </div>
            ) : !activeDoc ? (
              <div className="flex items-center justify-center py-20">
                <Loader2 className="w-6 h-6 animate-spin text-muted-foreground" />
              </div>
            ) : (
              <div>
                {/* Doc header */}
                <div className="bg-card border border-border rounded-xl p-5 mb-4">
                  <div className="flex items-start justify-between gap-4">
                    <div>
                      <h2 className="font-semibold">{activeDoc.title}</h2>
                      <div className="flex items-center gap-2 mt-1">
                        <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${STATUS_STYLES[activeDoc.status]}`}>
                          {activeDoc.status}
                          {activeDoc.status === "generating" && (
                            <Loader2 className="w-3 h-3 inline ml-1 animate-spin" />
                          )}
                        </span>
                        <span className="text-xs text-muted-foreground">{activeDoc.citation_style} citations</span>
                      </div>
                    </div>
                    <div className="flex items-center gap-2 shrink-0">
                      <button
                        onClick={() => generateAllMut.mutate(activeDoc.id)}
                        disabled={generateAllMut.isPending || activeDoc.status === "generating"}
                        className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-primary text-primary-foreground text-xs font-medium hover:opacity-90 disabled:opacity-60"
                      >
                        <Zap className="w-3.5 h-3.5" />
                        {activeDoc.status === "generating" ? "Generating…" : "Generate all"}
                      </button>
                      <a
                        href={documents.exportUrl(activeDoc.id)}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-border text-xs font-medium hover:bg-muted"
                      >
                        <Download className="w-3.5 h-3.5" /> DOCX
                      </a>
                    </div>
                  </div>
                </div>

                {/* Sections */}
                <div className="space-y-2">
                  {availableSections.map((section) => {
                    const content = generatedContent[section];
                    const isExpanded = expandedSections[section] ?? !!content;
                    const isGenerating = generatingSection === section;

                    return (
                      <div key={section} className="bg-card border border-border rounded-xl overflow-hidden">
                        <div
                          className="flex items-center justify-between p-4 cursor-pointer"
                          onClick={() => toggleSection(section)}
                        >
                          <div className="flex items-center gap-2">
                            {content ? (
                              <span className="w-2 h-2 rounded-full bg-green-500 shrink-0" />
                            ) : (
                              <span className="w-2 h-2 rounded-full bg-muted-foreground/30 shrink-0" />
                            )}
                            <span className="text-sm font-medium">{section}</span>
                            {!content && (
                              <span className="text-xs text-muted-foreground">Not yet generated</span>
                            )}
                          </div>
                          <div className="flex items-center gap-2">
                            <button
                              onClick={(e) => { e.stopPropagation(); handleGenerateSection(section); }}
                              disabled={isGenerating || activeDoc.status === "generating"}
                              className="flex items-center gap-1 px-2 py-1 rounded text-xs border border-border hover:bg-muted disabled:opacity-50"
                            >
                              {isGenerating ? (
                                <Loader2 className="w-3 h-3 animate-spin" />
                              ) : (
                                <RefreshCw className="w-3 h-3" />
                              )}
                              {content ? "Regenerate" : "Generate"}
                            </button>
                            {isExpanded
                              ? <ChevronUp className="w-4 h-4 text-muted-foreground" />
                              : <ChevronDown className="w-4 h-4 text-muted-foreground" />}
                          </div>
                        </div>
                        {isExpanded && content && (
                          <div className="px-4 pb-4 border-t border-border">
                            <p className="text-sm text-muted-foreground mt-3 whitespace-pre-wrap leading-relaxed">
                              {content}
                            </p>
                          </div>
                        )}
                      </div>
                    );
                  })}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </AppShell>
  );
}
