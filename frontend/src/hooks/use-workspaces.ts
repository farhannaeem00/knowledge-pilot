/**
 * First real data-fetching hooks via React Query - establishes the
 * pattern every later feature hook (documents, notes, chat, etc.)
 * follows: useQuery wrapping apiClient.get, useMutation wrapping
 * apiClient.post/patch/delete with query invalidation on success.
 */
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { apiClient } from "@/lib/api-client";
import type { Workspace } from "@/types/api";
import type { CreateWorkspaceFormValues } from "@/lib/schemas/workspace";

export function useWorkspaces() {
  return useQuery({
    queryKey: ["workspaces"],
    queryFn: () => apiClient.get<Workspace[]>("/workspaces"),
  });
}

export function useCreateWorkspace() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (values: CreateWorkspaceFormValues) => apiClient.post<Workspace>("/workspaces", values),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["workspaces"] });
    },
  });
}