"use client";

import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Search, Plus, Trash2, ExternalLink } from "lucide-react";
import { AppShell } from "@/components/layout/app-shell";
import { research } from "@/lib/api";

export default function ResearchPage() {
  const qc = useQueryClient();
  const [searchQuery, setSearchQuery] = useState("");
  const [searchResults, setSearchResults] = useState<any[]>([]);
  const [searching, setSearching] = useState(false);
  const [ingestQuery, setIngestQuery] = useState("");
  const [ingestDoi, setIngestDoi] = useState("");
  const [ingestMode, setIngestMode] = useState<"query" | "doi">("query");
  const [ingesting, setIngesting] = useState(false);
  const [ingestMsg, setIngestMsg] = useState("");

  const { data: library, isLoading: libLoading } = useQuery({
    queryKey: ["papers"],
    queryFn: () => research.list().then((r) => r.data),
  });

  const deleteMut = useMutation({
    mutationFn: (id: string) => research.remove(id),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["papers"] }),
  });

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!searchQuery.trim()) return;
    setSearching(true);
    try {
      const res = await research.search(searchQuery);
      setSearchResults(res.data);
    } catch { setSearchResults([]); }
    finally { setSearching(false); }
  };

  const handleIngest = async (e: React.FormEvent) => {
    e.preventDefault();
    setIngestMsg("");
    setIngesting(true);
    try {
      const payload = ingestMode === "doi"
        ? { doi: ingestDoi }
        : { query: ingestQuery, limit: 5 };
      const res = await research.ingest(payload);
      const count = Array.isArray(res.data) ? res.data.length : 1;
      setIngestMsg(`Ingested ${count} paper${count !== 1 ? "s" : ""} successfully.`);
      qc.invalidateQueries({ queryKey: ["papers"] });
      setIngestQuery(""); setIngestDoi("");
    } catch (err: any) {
      setIngestMsg(err?.response?.data?.detail || "Ingestion failed.");
    } finally { setIngesting(false); }
  };

  const PaperCard = ({ paper, score }: { paper: any; score?: number }) => (
    <div className="bg-card border border-border rounded-xl p-4">
      <div className="flex justify-between gap-4">
        <div className="flex-1 min-w-0">
          <div className="flex items-start gap-2 mb-1">
            <h3 className="font-medium text-sm leading-snug line-clamp-2">{paper.title}</h3>
            {score !== undefined && (
              <span className="shrink-0 text-xs px-1.5 py-0.5 rounded bg-green-100 text-green-700 font-medium">
                {Math.round(score * 100)}%
              </span>
            )}
          </div>
          <p className="text-xs text-muted-foreground mb-1">
            {paper.authors?.slice(0, 3).join(", ")}{paper.authors?.length > 3 ? " et al." : ""}
            {paper.year ? ` · ${paper.year}` : ""}
            {paper.source ? ` · ${paper.source.replace("_", " ")}` : ""}
          </p>
          {paper.abstract && (
            <p className="text-xs text-muted-foreground line-clamp-2">{paper.abstract}</p>
          )}
        </div>
        <div className="flex gap-1 shrink-0">
          {paper.url && (
            <a href={paper.url} target="_blank" rel="noopener noreferrer"
               className="p-1.5 rounded hover:bg-muted text-muted-foreground">
              <ExternalLink className="w-3.5 h-3.5" />
            </a>
          )}
          {paper.id && (
            <button onClick={() => deleteMut.mutate(paper.id)}
                    className="p-1.5 rounded hover:bg-muted text-muted-foreground hover:text-destructive">
              <Trash2 className="w-3.5 h-3.5" />
            </button>
          )}
        </div>
      </div>
    </div>
  );

  return (
    <AppShell>
      <div className="p-6 max-w-5xl mx-auto">
        <div className="mb-6">
          <h1 className="text-2xl font-bold">Research Library</h1>
          <p className="text-muted-foreground text-sm mt-1">
            Semantic search over your indexed academic papers
          </p>
        </div>

        <div className="grid md:grid-cols-2 gap-6 mb-8">
          {/* Semantic Search */}
          <div className="bg-card border border-border rounded-xl p-5">
            <h2 className="font-semibold mb-3">Search your library</h2>
            <form onSubmit={handleSearch} className="flex gap-2 mb-3">
              <input
                className="flex-1 px-3 py-2 rounded-lg border border-input bg-background text-sm focus:outline-none focus:ring-2 focus:ring-ring"
                placeholder="e.g. machine learning healthcare"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
              />
              <button type="submit" disabled={searching}
                      className="px-3 py-2 rounded-lg bg-primary text-primary-foreground text-sm disabled:opacity-60">
                <Search className="w-4 h-4" />
              </button>
            </form>
            {searching && <p className="text-sm text-muted-foreground">Searching…</p>}
            {searchResults.length > 0 && (
              <div className="space-y-2 max-h-80 overflow-y-auto">
                {searchResults.map((r: any) => (
                  <PaperCard key={r.paper.id} paper={r.paper} score={r.score} />
                ))}
              </div>
            )}
          </div>

          {/* Ingest */}
          <div className="bg-card border border-border rounded-xl p-5">
            <h2 className="font-semibold mb-3">Add papers</h2>
            <div className="flex gap-2 mb-3">
              {(["query", "doi"] as const).map((m) => (
                <button key={m} onClick={() => setIngestMode(m)}
                        className={`px-3 py-1 rounded-full text-xs font-medium transition-colors ${ingestMode === m ? "bg-primary text-primary-foreground" : "bg-muted text-muted-foreground"}`}>
                  {m === "query" ? "By topic" : "By DOI"}
                </button>
              ))}
            </div>
            <form onSubmit={handleIngest} className="space-y-2">
              {ingestMode === "query" ? (
                <input
                  className="w-full px-3 py-2 rounded-lg border border-input bg-background text-sm focus:outline-none focus:ring-2 focus:ring-ring"
                  placeholder="Topic to search (fetches top 5 papers)"
                  value={ingestQuery}
                  onChange={(e) => setIngestQuery(e.target.value)}
                />
              ) : (
                <input
                  className="w-full px-3 py-2 rounded-lg border border-input bg-background text-sm focus:outline-none focus:ring-2 focus:ring-ring"
                  placeholder="DOI e.g. 10.1145/3411764.3445377"
                  value={ingestDoi}
                  onChange={(e) => setIngestDoi(e.target.value)}
                />
              )}
              <button type="submit" disabled={ingesting}
                      className="flex items-center gap-2 px-4 py-2 rounded-lg bg-primary text-primary-foreground text-sm font-medium hover:opacity-90 disabled:opacity-60">
                <Plus className="w-4 h-4" />
                {ingesting ? "Fetching…" : "Ingest papers"}
              </button>
              {ingestMsg && (
                <p className="text-sm text-muted-foreground">{ingestMsg}</p>
              )}
            </form>
          </div>
        </div>

        {/* Library */}
        <div>
          <h2 className="font-semibold mb-3">
            Your library {library && `(${library.total} papers)`}
          </h2>
          {libLoading ? (
            <div className="space-y-3">{[1,2,3].map(i=><div key={i} className="h-24 bg-muted rounded-xl animate-pulse"/>)}</div>
          ) : library?.items.length === 0 ? (
            <div className="text-center py-12 text-muted-foreground text-sm">
              No papers yet. Add papers using the panel above.
            </div>
          ) : (
            <div className="space-y-3">
              {library?.items.map((p: any) => <PaperCard key={p.id} paper={p} />)}
            </div>
          )}
        </div>
      </div>
    </AppShell>
  );
}
