/**
 * Summary hooks. Polling the "active" endpoint works because the
 * backend marks a newly-created summary is_active=True immediately on
 * creation (status "pending"), so polling that same endpoint sees the
 * status progress: pending -> processing -> done, without needing a
 * separate get-by-id endpoint.
 */
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { apiClient, ApiRequestError } from "@/lib/api-client";
import type { Summary } from "@/types/api";

export type SummaryStyle =
  | "executive"
  | "beginner"
  | "technical"
  | "bullet_points"
  | "detailed"
  | "academic"
  | "content_creator";

export function useActiveSummary(workspaceId: string, documentId: string, style: SummaryStyle) {
  return useQuery({
    queryKey: ["summary-active", workspaceId, documentId, style],
    queryFn: () =>
      apiClient.get<Summary>(`/workspaces/${workspaceId}/documents/${documentId}/summaries/active?style=${style}`),
    enabled: !!workspaceId && !!documentId,
    retry: (failureCount, error) => {
      // A 404 means "no summary generated yet for this style" - not a
      // transient error worth retrying.
      if (error instanceof ApiRequestError && error.status === 404) return false;
      return failureCount < 2;
    },
    refetchInterval: (query) => {
      const status = query.state.data?.status;
      return status === "pending" || status === "processing" ? 2500 : false;
    },
  });
}

export function useGenerateSummary(workspaceId: string, documentId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (style: SummaryStyle) =>
      apiClient.post<Summary>(`/workspaces/${workspaceId}/documents/${documentId}/summaries`, { style }),
    onSuccess: (_data, style) => {
      queryClient.invalidateQueries({ queryKey: ["summary-active", workspaceId, documentId, style] });
    },
  });
}