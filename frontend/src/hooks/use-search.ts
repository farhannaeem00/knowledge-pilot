/**
 * Search hook - debounced, mode-switchable (hybrid/semantic/keyword).
 * Query is disabled while the debounced term is empty, so we don't fire
 * a request for an empty string on page load.
 */
import { useQuery } from "@tanstack/react-query";
import { useEffect, useState } from "react";
import { apiClient } from "@/lib/api-client";

export type SearchMode = "hybrid" | "semantic" | "keyword";

export interface SearchResult {
  result_type: "document_chunk" | "note" | "summary";
  id: string;
  workspace_id: string;
  document_id: string | null;
  title: string;
  snippet: string;
  score: number;
}

interface SearchResponse {
  query: string;
  mode: SearchMode;
  results: SearchResult[];
}

export function useDebouncedValue<T>(value: T, delayMs: number): T {
  const [debounced, setDebounced] = useState(value);
  useEffect(() => {
    const timer = setTimeout(() => setDebounced(value), delayMs);
    return () => clearTimeout(timer);
  }, [value, delayMs]);
  return debounced;
}

export function useSearch(query: string, mode: SearchMode) {
  const debouncedQuery = useDebouncedValue(query, 400);

  return useQuery({
    queryKey: ["search", debouncedQuery, mode],
    queryFn: () =>
      apiClient.get<SearchResponse>(
        `/search?q=${encodeURIComponent(debouncedQuery)}&mode=${mode}&limit=20`
      ),
    enabled: debouncedQuery.trim().length > 0,
  });
}