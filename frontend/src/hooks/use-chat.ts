/**
 * Chat hooks. No polling here (unlike summaries/scripts) - the backend
 * chat endpoint is synchronous: it does retrieval + the Groq call and
 * returns the assistant's reply directly in the response, so a plain
 * mutation is the correct shape, not a poll loop.
 */
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { apiClient } from "@/lib/api-client";
import type { ChatMessage, ChatThread } from "@/types/api";

export function useChatThreads(workspaceId: string, documentId: string) {
  return useQuery({
    queryKey: ["chat-threads", workspaceId, documentId],
    queryFn: () => apiClient.get<ChatThread[]>(`/workspaces/${workspaceId}/documents/${documentId}/chat/threads`),
    enabled: !!workspaceId && !!documentId,
  });
}

export function useCreateThread(workspaceId: string, documentId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (title: string) =>
      apiClient.post<ChatThread>(`/workspaces/${workspaceId}/documents/${documentId}/chat/threads`, { title }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["chat-threads", workspaceId, documentId] });
    },
  });
}

export function useChatMessages(workspaceId: string, documentId: string, threadId: string | null) {
  return useQuery({
    queryKey: ["chat-messages", workspaceId, documentId, threadId],
    queryFn: () =>
      apiClient.get<ChatMessage[]>(
        `/workspaces/${workspaceId}/documents/${documentId}/chat/threads/${threadId}/messages`
      ),
    enabled: !!workspaceId && !!documentId && !!threadId,
  });
}

export function useSendMessage(workspaceId: string, documentId: string, threadId: string | null) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (content: string) =>
      apiClient.post<ChatMessage>(
        `/workspaces/${workspaceId}/documents/${documentId}/chat/threads/${threadId}/messages`,
        { content }
      ),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["chat-messages", workspaceId, documentId, threadId] });
    },
  });
}