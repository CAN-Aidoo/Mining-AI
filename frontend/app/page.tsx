import Link from "next/link";

const modules = [
  {
    title: "Research Library",
    description: "Search 500+ open-access academic papers with semantic AI",
    href: "/research",
    icon: "🔬",
    status: "Week 3",
  },
  {
    title: "Documentation Engine",
    description: "Generate complete academic documents with verified citations",
    href: "/documents",
    icon: "📄",
    status: "Week 4",
  },
  {
    title: "Prototype Builder",
    description: "Build and deploy working software demos automatically",
    href: "/prototypes",
    icon: "⚙️",
    status: "Week 5",
  },
  {
    title: "Projects",
    description: "Manage your final year projects end-to-end",
    href: "/projects",
    icon: "🗂️",
    status: "Week 2",
  },
];

export default function HomePage() {
  return (
    <main className="min-h-screen bg-background">
      <div className="container mx-auto px-4 py-16 max-w-4xl">
        {/* Header */}
        <div className="text-center mb-16">
          <h1 className="text-4xl font-bold tracking-tight text-foreground mb-4">
            Mining AI Platform
          </h1>
          <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
            From project idea to full documentation and working prototype —
            in under 30 minutes.
          </p>
          <div className="mt-6 flex items-center justify-center gap-3">
            <span className="inline-flex items-center rounded-full bg-green-100 px-3 py-1 text-sm font-medium text-green-700">
              ✓ Infrastructure Ready
            </span>
            <span className="inline-flex items-center rounded-full bg-blue-100 px-3 py-1 text-sm font-medium text-blue-700">
              Week 1 Scaffold
            </span>
          </div>
        </div>

        {/* Module Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {modules.map((module) => (
            <Link
              key={module.href}
              href={module.href}
              className="group block rounded-lg border border-border bg-card p-6 hover:border-primary hover:shadow-md transition-all duration-200"
            >
              <div className="flex items-start gap-4">
                <span className="text-3xl">{module.icon}</span>
                <div className="flex-1">
                  <div className="flex items-center justify-between mb-1">
                    <h2 className="text-lg font-semibold text-card-foreground group-hover:text-primary transition-colors">
                      {module.title}
                    </h2>
                    <span className="text-xs text-muted-foreground bg-muted px-2 py-0.5 rounded">
                      {module.status}
                    </span>
                  </div>
                  <p className="text-sm text-muted-foreground">
                    {module.description}
                  </p>
                </div>
              </div>
            </Link>
          ))}
        </div>

        {/* API Status Footer */}
        <div className="mt-16 text-center text-sm text-muted-foreground border-t pt-8">
          <p className="mb-2 font-medium">Development Links</p>
          <div className="flex justify-center gap-6">
            <a
              href="http://localhost:8000/health"
              target="_blank"
              rel="noopener noreferrer"
              className="text-primary hover:underline"
            >
              API Health ↗
            </a>
            <a
              href="http://localhost:8000/docs"
              target="_blank"
              rel="noopener noreferrer"
              className="text-primary hover:underline"
            >
              Swagger UI ↗
            </a>
            <a
              href="http://localhost:8001/api/v1/heartbeat"
              target="_blank"
              rel="noopener noreferrer"
              className="text-primary hover:underline"
            >
              ChromaDB ↗
            </a>
          </div>
        </div>
      </div>
    </main>
  );
}
