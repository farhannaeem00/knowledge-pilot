/**
 * Folder hooks - workspace-scoped, simple flat list for now (backend
 * supports parent_id hierarchy, but a nested tree UI is a future
 * enhancement; this treats folders as one flat list, which still
 * covers "organize documents into named groups").
 */
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { apiClient } from "@/lib/api-client";

export interface Folder {
  id: string;
  workspace_id: string;
  parent_id: string | null;
  name: string;
  created_at: string;
}

export function useFolders(workspaceId: string) {
  return useQuery({
    queryKey: ["folders", workspaceId],
    queryFn: () => apiClient.get<Folder[]>(`/workspaces/${workspaceId}/folders`),
    enabled: !!workspaceId,
  });
}

export function useCreateFolder(workspaceId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (name: string) => apiClient.post<Folder>(`/workspaces/${workspaceId}/folders`, { name }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["folders", workspaceId] }),
  });
}

export function useDeleteFolder(workspaceId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (folderId: string) => apiClient.delete<void>(`/workspaces/${workspaceId}/folders/${folderId}`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["folders", workspaceId] });
      queryClient.invalidateQueries({ queryKey: ["documents", workspaceId] });
    },
  });
}