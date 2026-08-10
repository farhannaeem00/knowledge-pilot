/**
 * Note hooks - workspace-scoped CRUD, matching the backend's design
 * (notes persist across document versions, not tied to one document).
 */
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { apiClient } from "@/lib/api-client";
import type { Note } from "@/types/api";

export interface NoteCreateInput {
  title: string;
  content_md: string;
  tags: string[];
  document_id?: string | null;
}

export interface NoteUpdateInput {
  title?: string;
  content_md?: string;
  tags?: string[];
  is_pinned?: boolean;
}

export function useNotes(workspaceId: string) {
  return useQuery({
    queryKey: ["notes", workspaceId],
    queryFn: () => apiClient.get<Note[]>(`/workspaces/${workspaceId}/notes`),
    enabled: !!workspaceId,
  });
}

export function useCreateNote(workspaceId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (input: NoteCreateInput) => apiClient.post<Note>(`/workspaces/${workspaceId}/notes`, input),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["notes", workspaceId] }),
  });
}

export function useUpdateNote(workspaceId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ noteId, input }: { noteId: string; input: NoteUpdateInput }) =>
      apiClient.patch<Note>(`/workspaces/${workspaceId}/notes/${noteId}`, input),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["notes", workspaceId] }),
  });
}

export function useDeleteNote(workspaceId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (noteId: string) => apiClient.delete<void>(`/workspaces/${workspaceId}/notes/${noteId}`),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["notes", workspaceId] }),
  });
}