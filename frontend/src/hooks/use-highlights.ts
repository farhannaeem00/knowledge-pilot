/**
 * Highlight hooks - version-scoped (anchored to a specific document
 * version's text), matching the backend design.
 */
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { apiClient } from "@/lib/api-client";
import type { Highlight } from "@/types/api";

export interface HighlightCreateInput {
  level: "must_read" | "important" | "optional" | "custom";
  start_offset: number;
  end_offset: number;
  highlighted_text: string;
  note?: string | null;
}

export function useHighlights(workspaceId: string, documentId: string) {
  return useQuery({
    queryKey: ["highlights", workspaceId, documentId],
    queryFn: () => apiClient.get<Highlight[]>(`/workspaces/${workspaceId}/documents/${documentId}/highlights`),
    enabled: !!workspaceId && !!documentId,
  });
}

export function useCreateHighlight(workspaceId: string, documentId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (input: HighlightCreateInput) =>
      apiClient.post<Highlight>(`/workspaces/${workspaceId}/documents/${documentId}/highlights`, input),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["highlights", workspaceId, documentId] }),
  });
}

export function useDeleteHighlight(workspaceId: string, documentId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (highlightId: string) =>
      apiClient.delete<void>(`/workspaces/${workspaceId}/documents/${documentId}/highlights/${highlightId}`),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["highlights", workspaceId, documentId] }),
  });
}