"use client";

import { useState } from "react";
import { Search as SearchIcon } from "lucide-react";
import { useSearch, type SearchMode } from "@/hooks/use-search";
import { SearchResultItem } from "@/components/search/search-result-item";
import { Input } from "@/components/ui/input";
import { Skeleton } from "@/components/ui/skeleton";
import { cn } from "@/lib/utils";

const MODES: { key: SearchMode; label: string }[] = [
  { key: "hybrid", label: "Hybrid" },
  { key: "semantic", label: "Semantic" },
  { key: "keyword", label: "Keyword" },
];

export default function SearchPage() {
  const [query, setQuery] = useState("");
  const [mode, setMode] = useState<SearchMode>("hybrid");
  const { data, isLoading, isFetching } = useSearch(query, mode);

  return (
    <div className="mx-auto max-w-3xl space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Search</h1>
        <p className="text-muted-foreground">Search across your documents, notes, and summaries.</p>
      </div>

      <div className="space-y-3">
        <div className="relative">
          <SearchIcon className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
          <Input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search everything..."
            className="pl-9"
            autoFocus
          />
        </div>

        <div className="flex gap-1">
          {MODES.map((m) => (
            <button
              key={m.key}
              onClick={() => setMode(m.key)}
              className={cn(
                "rounded-md px-3 py-1 text-sm font-medium transition-colors",
                mode === m.key
                  ? "bg-primary text-primary-foreground"
                  : "text-muted-foreground hover:bg-accent hover:text-accent-foreground"
              )}
            >
              {m.label}
            </button>
          ))}
        </div>
      </div>

      {query.trim().length === 0 ? (
        <p className="py-12 text-center text-sm text-muted-foreground">
          Start typing to search across your workspaces.
        </p>
      ) : isLoading || isFetching ? (
        <div className="space-y-2">
          <Skeleton className="h-20 w-full" />
          <Skeleton className="h-20 w-full" />
        </div>
      ) : data && data.results.length > 0 ? (
        <div className="space-y-2">
          <p className="text-xs text-muted-foreground">
            {data.results.length} result{data.results.length === 1 ? "" : "s"}
          </p>
          {data.results.map((result) => (
            <SearchResultItem key={`${result.result_type}-${result.id}`} result={result} />
          ))}
        </div>
      ) : (
        <p className="py-12 text-center text-sm text-muted-foreground">
          No results found for &quot;{query}&quot;.
        </p>
      )}
    </div>
  );
}