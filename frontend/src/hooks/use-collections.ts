/**
 * Collection hooks - workspace-scoped, with membership management.
 * Membership endpoints return 204/no body on success (matching the
 * backend), so those mutations just invalidate the documents-in-
 * collection query rather than expecting a response payload.
 */
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { apiClient } from "@/lib/api-client";
import type { Document } from "@/types/api";

export interface Collection {
  id: string;
  workspace_id: string;
  name: string;
  created_at: string;
}

export function useCollections(workspaceId: string) {
  return useQuery({
    queryKey: ["collections", workspaceId],
    queryFn: () => apiClient.get<Collection[]>(`/workspaces/${workspaceId}/collections`),
    enabled: !!workspaceId,
  });
}

export function useCreateCollection(workspaceId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (name: string) => apiClient.post<Collection>(`/workspaces/${workspaceId}/collections`, { name }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["collections", workspaceId] }),
  });
}

export function useCollectionDocuments(workspaceId: string, collectionId: string | null) {
  return useQuery({
    queryKey: ["collection-documents", workspaceId, collectionId],
    queryFn: () => apiClient.get<Document[]>(`/workspaces/${workspaceId}/collections/${collectionId}/documents`),
    enabled: !!workspaceId && !!collectionId,
  });
}

export function useAddDocumentToCollection(workspaceId: string, collectionId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (documentId: string) =>
      apiClient.post<void>(`/workspaces/${workspaceId}/collections/${collectionId}/documents`, {
        document_id: documentId,
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["collection-documents", workspaceId, collectionId] });
    },
  });
}

export function useRemoveDocumentFromCollection(workspaceId: string, collectionId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (documentId: string) =>
      apiClient.delete<void>(`/workspaces/${workspaceId}/collections/${collectionId}/documents/${documentId}`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["collection-documents", workspaceId, collectionId] });
    },
  });
}