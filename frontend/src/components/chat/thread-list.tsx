"use client";

import { useState } from "react";
import { Plus, MessageSquare } from "lucide-react";
import { cn } from "@/lib/utils";
import { useChatThreads, useCreateThread } from "@/hooks/use-chat";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Skeleton } from "@/components/ui/skeleton";

export function ThreadList({
  workspaceId,
  documentId,
  activeThreadId,
  onSelectThread,
}: {
  workspaceId: string;
  documentId: string;
  activeThreadId: string | null;
  onSelectThread: (threadId: string) => void;
}) {
  const { data: threads, isLoading } = useChatThreads(workspaceId, documentId);
  const createThread = useCreateThread(workspaceId, documentId);
  const [newTitle, setNewTitle] = useState("");
  const [showInput, setShowInput] = useState(false);

  const handleCreate = () => {
    const title = newTitle.trim() || "New Chat";
    createThread.mutate(title, {
      onSuccess: (thread) => {
        onSelectThread(thread.id);
        setNewTitle("");
        setShowInput(false);
      },
    });
  };

  return (
    <div className="flex w-64 shrink-0 flex-col border-r border-border">
      <div className="border-b border-border p-3">
        {showInput ? (
          <div className="space-y-2">
            <Input
              autoFocus
              placeholder="Thread name"
              value={newTitle}
              onChange={(e) => setNewTitle(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && handleCreate()}
            />
            <div className="flex gap-2">
              <Button size="sm" onClick={handleCreate} disabled={createThread.isPending}>
                Create
              </Button>
              <Button size="sm" variant="ghost" onClick={() => setShowInput(false)}>
                Cancel
              </Button>
            </div>
          </div>
        ) : (
          <Button size="sm" className="w-full" onClick={() => setShowInput(true)}>
            <Plus className="mr-1 h-3.5 w-3.5" />
            New Thread
          </Button>
        )}
      </div>

      <div className="flex-1 space-y-1 overflow-y-auto p-2">
        {isLoading ? (
          <>
            <Skeleton className="h-9 w-full" />
            <Skeleton className="h-9 w-full" />
          </>
        ) : threads && threads.length > 0 ? (
          threads.map((thread) => (
            <button
              key={thread.id}
              onClick={() => onSelectThread(thread.id)}
              className={cn(
                "flex w-full items-center gap-2 rounded-md px-3 py-2 text-left text-sm transition-colors",
                activeThreadId === thread.id
                  ? "bg-primary text-primary-foreground"
                  : "text-muted-foreground hover:bg-accent hover:text-accent-foreground"
              )}
            >
              <MessageSquare className="h-3.5 w-3.5 shrink-0" />
              <span className="truncate">{thread.title}</span>
            </button>
          ))
        ) : (
          <p className="p-3 text-center text-xs text-muted-foreground">No threads yet. Create one to start chatting.</p>
        )}
      </div>
    </div>
  );
}