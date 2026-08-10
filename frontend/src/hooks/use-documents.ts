/**
 * Document hooks for a given workspace: list, upload (multipart), and
 * status polling for a single document (used while a version is still
 * processing - refetchInterval stops automatically once status is
 * "done"/"failed"/"failed_partial").
 */
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { apiClient } from "@/lib/api-client";
import type { Document, DocumentWithVersions } from "@/types/api";

export function useDocuments(workspaceId: string) {
  return useQuery({
    queryKey: ["documents", workspaceId],
    queryFn: () => apiClient.get<Document[]>(`/workspaces/${workspaceId}/documents`),
    enabled: !!workspaceId,
  });
}

export function useDocument(workspaceId: string, documentId: string | undefined) {
  return useQuery({
    queryKey: ["document", workspaceId, documentId],
    queryFn: () => apiClient.get<DocumentWithVersions>(`/workspaces/${workspaceId}/documents/${documentId}`),
    enabled: !!workspaceId && !!documentId,
    refetchInterval: (query) => {
      const currentVersion = query.state.data?.versions.find((v) => v.is_current);
      const isProcessing = currentVersion?.status === "processing" || currentVersion?.status === "uploaded";
      return isProcessing ? 3000 : false;
    },
  });
}

export function useUploadDocument(workspaceId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (file: File) => {
      const formData = new FormData();
      formData.append("file", file);
      return apiClient.postForm<Document>(`/workspaces/${workspaceId}/documents`, formData);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["documents", workspaceId] });
    },
  });
}