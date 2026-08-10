"use client";

import { Folder as FolderIcon, FolderOpen, Trash2, Inbox } from "lucide-react";
import { cn } from "@/lib/utils";
import { useFolders, useDeleteFolder } from "@/hooks/use-folders";
import { CreateFolderDialog } from "./create-folder-dialog";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";

export function FolderSidebar({
  workspaceId,
  activeFolderId,
  onSelectFolder,
}: {
  workspaceId: string;
  activeFolderId: string | null;
  onSelectFolder: (folderId: string | null) => void;
}) {
  const { data: folders, isLoading } = useFolders(workspaceId);
  const deleteFolder = useDeleteFolder(workspaceId);

  return (
    <div className="w-52 shrink-0 space-y-3">
      <CreateFolderDialog workspaceId={workspaceId} />

      <div className="space-y-1">
        <button
          onClick={() => onSelectFolder(null)}
          className={cn(
            "flex w-full items-center gap-2 rounded-md px-2.5 py-1.5 text-sm transition-colors",
            activeFolderId === null
              ? "bg-primary text-primary-foreground"
              : "text-muted-foreground hover:bg-accent hover:text-accent-foreground"
          )}
        >
          <Inbox className="h-3.5 w-3.5" />
          All Documents
        </button>

        {isLoading ? (
          <Skeleton className="h-8 w-full" />
        ) : (
          folders?.map((folder) => {
            const isActive = activeFolderId === folder.id;
            return (
              <div
                key={folder.id}
                className={cn(
                  "group flex items-center justify-between rounded-md px-2.5 py-1.5 text-sm transition-colors",
                  isActive
                    ? "bg-primary text-primary-foreground"
                    : "text-muted-foreground hover:bg-accent hover:text-accent-foreground"
                )}
              >
                <button onClick={() => onSelectFolder(folder.id)} className="flex min-w-0 flex-1 items-center gap-2">
                  {isActive ? <FolderOpen className="h-3.5 w-3.5 shrink-0" /> : <FolderIcon className="h-3.5 w-3.5 shrink-0" />}
                  <span className="truncate">{folder.name}</span>
                </button>
                <Button
                  size="icon"
                  variant="ghost"
                  className={cn("h-5 w-5 shrink-0 opacity-0 group-hover:opacity-100", isActive && "text-primary-foreground hover:text-primary-foreground")}
                  onClick={() => {
                    if (activeFolderId === folder.id) onSelectFolder(null);
                    deleteFolder.mutate(folder.id);
                  }}
                >
                  <Trash2 className="h-3 w-3" />
                </Button>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
}