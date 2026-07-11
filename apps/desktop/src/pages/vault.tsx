import { useState } from "react";
import { UploadCloud, FileText, Database, ShieldAlert } from "lucide-react";
import { SyncConflictPanel } from "../components/shared/sync-conflict-panel";

interface VaultDocument {
  name: string;
  size: string;
  chunks: number;
  dateIndexed: string;
}

export function VaultPage() {
  const [searchQuery, setSearchQuery] = useState("");
  const [documents, setDocuments] = useState<VaultDocument[]>([
    { name: "System Architecture & Scheduler Rules.pdf", size: "1.2 MB", chunks: 48, dateIndexed: "2026-07-06" },
    { name: "Q3 Project Alignment Goals.docx", size: "420 KB", chunks: 18, dateIndexed: "2026-07-05" },
    { name: "Telegram Bot API Guidelines.md", size: "45 KB", chunks: 6, dateIndexed: "2026-07-08" },
    { name: "Personal Scheduling Constraints.txt", size: "12 KB", chunks: 2, dateIndexed: "2026-07-09" }
  ]);
  const [isSearching, setIsSearching] = useState(false);
  const [searchResult, setSearchResult] = useState<string | null>(null);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (!searchQuery.trim()) return;

    setIsSearching(true);
    setTimeout(() => {
      setIsSearching(false);
      setSearchResult(
        `Found 3 relevant snippets in "System Architecture & Scheduler Rules.pdf" and "Personal Scheduling Constraints.txt". Semantic matching confidence: 94%.`
      );
    }, 800);
  };

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    const newDoc: VaultDocument = {
      name: file.name,
      size: `${(file.size / 1024).toFixed(0)} KB`,
      chunks: Math.floor(Math.random() * 10) + 1,
      dateIndexed: new Date().toISOString().split("T")[0]
    };

    setDocuments([newDoc, ...documents]);
  };

  return (
    <div className="p-8 max-w-6xl mx-auto">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-semibold text-foreground">Context Vault</h1>
        <p className="text-sm text-muted-foreground mt-1">
          Semantic vector index and long-term project memory
        </p>
      </div>

      {/* Main Content Grid */}
      <div className="grid grid-cols-3 gap-8">
        {/* Left Columns: Knowledge base & Uploads */}
        <div className="col-span-2 space-y-6">
          {/* RAG Vector Search */}
          <div className="bg-card border border-border rounded-xl p-6">
            <div className="flex items-center gap-2 mb-4">
              <Database className="w-5 h-5 text-primary" />
              <h2 className="text-sm font-semibold text-foreground">Search Knowledge Base</h2>
            </div>
            
            <form onSubmit={handleSearch} className="flex gap-2">
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Query context e.g., 'What are my preferences for peak hours?'"
                className="flex-1 bg-input border border-border rounded-lg px-4 py-2.5 text-sm text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary/50"
              />
              <button
                type="submit"
                disabled={isSearching}
                className="px-5 py-2.5 bg-primary text-primary-foreground hover:bg-primary/90 rounded-lg text-sm font-semibold transition-colors flex items-center gap-1.5"
              >
                {isSearching ? "Searching..." : "Search"}
              </button>
            </form>

            {searchResult && (
              <div className="mt-4 p-4 bg-primary/5 border border-primary/20 rounded-lg text-xs text-foreground leading-relaxed">
                {searchResult}
              </div>
            )}
          </div>

          {/* File Upload & Indexed Documents */}
          <div className="bg-card border border-border rounded-xl p-6">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-sm font-semibold text-foreground">Indexed Context Documents</h2>
              
              {/* File Upload Input */}
              <label className="px-3 py-1.5 bg-muted hover:bg-muted/80 text-foreground border border-border rounded-lg text-xs font-semibold flex items-center gap-2 cursor-pointer transition-colors">
                <UploadCloud className="w-4 h-4 text-muted-foreground" />
                Upload Doc
                <input
                  type="file"
                  onChange={handleFileUpload}
                  className="hidden"
                  accept=".txt,.pdf,.md,.docx"
                />
              </label>
            </div>

            <div className="space-y-3">
              {documents.map((doc, idx) => (
                <div
                  key={idx}
                  className="flex items-center justify-between p-3.5 bg-muted/30 border border-border rounded-lg hover:border-primary/20 transition-colors"
                >
                  <div className="flex items-center gap-3">
                    <div className="p-2 bg-muted rounded-lg text-muted-foreground">
                      <FileText className="w-4 h-4" />
                    </div>
                    <div>
                      <p className="text-xs font-semibold text-foreground truncate max-w-sm">{doc.name}</p>
                      <p className="text-[10px] text-muted-foreground mt-0.5">{doc.size} | {doc.chunks} vector chunks</p>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="text-[10px] text-muted-foreground">Indexed on</p>
                    <p className="text-[10px] text-foreground font-semibold mt-0.5">{doc.dateIndexed}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Right Column: Sync conflict panel (Sprint 12/20) */}
        <div className="col-span-1 space-y-6">
          <div className="bg-card border border-border rounded-xl p-6">
            <div className="flex items-center gap-2 mb-4 border-b border-border pb-4">
              <ShieldAlert className="w-5 h-5 text-amber-400" />
              <h2 className="text-sm font-semibold text-foreground">Sync Center</h2>
            </div>
            <SyncConflictPanel />
          </div>
        </div>
      </div>
    </div>
  );
}
