import Link from "next/link";
import { FolderKanban } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import type { Workspace } from "@/types/api";
import { formatDistanceToNow } from "date-fns";

export function WorkspaceCard({ workspace }: { workspace: Workspace }) {
  return (
    <Link href={`/workspaces/${workspace.id}`}>
      <Card className="transition-colors hover:border-primary">
        <CardContent className="flex items-start gap-3 p-4">
          <div className="rounded-md bg-primary/10 p-2">
            <FolderKanban className="h-5 w-5 text-primary" />
          </div>
          <div className="min-w-0 flex-1">
            <div className="flex items-center gap-2">
              <p className="truncate font-medium">{workspace.name}</p>
              <Badge variant="secondary" className="capitalize">
                {workspace.status}
              </Badge>
            </div>
            <p className="text-xs text-muted-foreground">
              Updated {formatDistanceToNow(new Date(workspace.updated_at), { addSuffix: true })}
            </p>
          </div>
        </CardContent>
      </Card>
    </Link>
  );
}