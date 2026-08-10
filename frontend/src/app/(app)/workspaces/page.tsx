"use client";

import { useWorkspaces } from "@/hooks/use-workspaces";
import { WorkspaceCard } from "@/components/workspaces/workspace-card";
import { CreateWorkspaceDialog } from "@/components/workspaces/create-workspace-dialog";
import { Skeleton } from "@/components/ui/skeleton";
import { FolderKanban } from "lucide-react";

export default function WorkspacesPage() {
  const { data: workspaces, isLoading, isError } = useWorkspaces();

  return (
    <div className="mx-auto max-w-5xl space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Workspaces</h1>
          <p className="text-muted-foreground">Organize your documents, chats, and notes.</p>
        </div>
        <CreateWorkspaceDialog />
      </div>

      {isLoading ? (
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {[1, 2, 3].map((i) => (
            <Skeleton key={i} className="h-24 w-full" />
          ))}
        </div>
      ) : isError ? (
        <p className="text-sm text-destructive">Failed to load workspaces.</p>
      ) : workspaces && workspaces.length > 0 ? (
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {workspaces.map((ws) => (
            <WorkspaceCard key={ws.id} workspace={ws} />
          ))}
        </div>
      ) : (
        <div className="flex flex-col items-center justify-center gap-3 rounded-lg border border-dashed border-border py-16 text-center">
          <FolderKanban className="h-10 w-10 text-muted-foreground" />
          <p className="text-muted-foreground">No workspaces yet.</p>
          <CreateWorkspaceDialog />
        </div>
      )}
    </div>
  );
}