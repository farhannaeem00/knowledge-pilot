/**
 * Script hooks. Unlike summaries (one "active" per style), scripts have
 * no active/history distinction in the backend - every generation is
 * just a new row. So we list all scripts for the document and let the
 * UI filter/display by platform, polling only the most recent one while
 * it's still pending/processing.
 */
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { apiClient } from "@/lib/api-client";
import type { Script } from "@/types/api";

export type ScriptPlatform =
  | "youtube"
  | "linkedin"
  | "instagram_reel"
  | "tiktok"
  | "podcast"
  | "presentation";

export function useScripts(workspaceId: string, documentId: string) {
  return useQuery({
    queryKey: ["scripts", workspaceId, documentId],
    queryFn: () => apiClient.get<Script[]>(`/workspaces/${workspaceId}/documents/${documentId}/scripts`),
    enabled: !!workspaceId && !!documentId,
    refetchInterval: (query) => {
      const scripts = query.state.data;
      const anyPending = scripts?.some((s) => s.status === "pending" || s.status === "processing");
      return anyPending ? 2500 : false;
    },
  });
}

export function useGenerateScript(workspaceId: string, documentId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (platform: ScriptPlatform) =>
      apiClient.post<Script>(`/workspaces/${workspaceId}/documents/${documentId}/scripts`, { platform }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["scripts", workspaceId, documentId] });
    },
  });
}