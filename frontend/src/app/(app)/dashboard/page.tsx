"use client";

import Link from "next/link";
import { FileText, MessageSquare, FolderKanban, StickyNote, Video, Plus } from "lucide-react";
import { useWorkspaces } from "@/hooks/use-workspaces";
import { useQuery } from "@tanstack/react-query";
import { apiClient } from "@/lib/api-client";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { Button } from "@/components/ui/button";
import { useAuthStore } from "@/store/auth-store";
import type { Document, ChatThread, Note } from "@/types/api";

/**
 * Dashboard stat counts. Each workspace's documents/chat-threads/notes
 * are fetched and summed client-side - there's no single "all my stuff"
 * backend endpoint, so we fan out per-workspace. Fine at this scale
 * (a handful of workspaces); would move server-side if that changes.
 */
function useDashboardCounts(workspaceIds: string[]) {
  return useQuery({
    queryKey: ["dashboard-counts", workspaceIds],
    queryFn: async () => {
      let documentCount = 0;
      let noteCount = 0;
      let chatThreadCount = 0;

      for (const workspaceId of workspaceIds) {
        const [documents, notes] = await Promise.all([
          apiClient.get<Document[]>(`/workspaces/${workspaceId}/documents`),
          apiClient.get<Note[]>(`/workspaces/${workspaceId}/notes`),
        ]);
        documentCount += documents.length;
        noteCount += notes.length;

        // Chat threads are per-document, so fan out one more level.
        const threadCounts = await Promise.all(
          documents.map((doc) =>
            apiClient
              .get<ChatThread[]>(`/workspaces/${workspaceId}/documents/${doc.id}/chat/threads`)
              .then((threads) => threads.length)
              .catch(() => 0)
          )
        );
        chatThreadCount += threadCounts.reduce((sum, n) => sum + n, 0);
      }

      return { documentCount, noteCount, chatThreadCount };
    },
    enabled: workspaceIds.length > 0,
  });
}

export default function DashboardPage() {
  const user = useAuthStore((s) => s.user);
  const { data: workspaces, isLoading: workspacesLoading } = useWorkspaces();
  const workspaceIds = (workspaces ?? []).map((w) => w.id);
  const { data: counts, isLoading: countsLoading } = useDashboardCounts(workspaceIds);

  return (
    <div className="mx-auto max-w-6xl space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Welcome back{user?.full_name ? `, ${user.full_name}` : ""}</h1>
        <p className="text-muted-foreground">Here&apos;s what&apos;s happening in your workspaces.</p>
      </div>

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatCard
          icon={FolderKanban}
          label="Workspaces"
          value={workspacesLoading ? undefined : workspaces?.length ?? 0}
        />
        <StatCard
          icon={FileText}
          label="Documents"
          value={workspaceIds.length === 0 ? 0 : countsLoading ? undefined : counts?.documentCount ?? 0}
        />
        <StatCard
          icon={MessageSquare}
          label="Chat threads"
          value={workspaceIds.length === 0 ? 0 : countsLoading ? undefined : counts?.chatThreadCount ?? 0}
        />
        <StatCard
          icon={StickyNote}
          label="Notes"
          value={workspaceIds.length === 0 ? 0 : countsLoading ? undefined : counts?.noteCount ?? 0}
        />
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between">
            <CardTitle className="text-base">Your Workspaces</CardTitle>
            <Button size="sm" variant="outline" asChild>
              <Link href="/workspaces">
                <Plus className="mr-1 h-3.5 w-3.5" />
                New
              </Link>
            </Button>
          </CardHeader>
          <CardContent>
            {workspacesLoading ? (
              <div className="space-y-2">
                <Skeleton className="h-10 w-full" />
                <Skeleton className="h-10 w-full" />
              </div>
            ) : workspaces && workspaces.length > 0 ? (
              <ul className="space-y-2">
                {workspaces.slice(0, 5).map((ws) => (
                  <li key={ws.id}>
                    <Link
                      href={`/workspaces/${ws.id}`}
                      className="flex items-center justify-between rounded-md border border-border px-3 py-2 text-sm hover:bg-accent"
                    >
                      <span>{ws.name}</span>
                      <span className="text-xs capitalize text-muted-foreground">{ws.status}</span>
                    </Link>
                  </li>
                ))}
              </ul>
            ) : (
              <EmptyState message="No workspaces yet." ctaHref="/workspaces" ctaLabel="Create your first workspace" />
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-base">Recent Video Scripts</CardTitle>
          </CardHeader>
          <CardContent>
            <EmptyState message="Video scripts you generate will show up here." icon={Video} />
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

function StatCard({
  icon: Icon,
  label,
  value,
}: {
  icon: React.ComponentType<{ className?: string }>;
  label: string;
  value: number | undefined;
}) {
  return (
    <Card>
      <CardContent className="flex items-center gap-4 p-4">
        <div className="rounded-md bg-primary/10 p-2">
          <Icon className="h-5 w-5 text-primary" />
        </div>
        <div>
          <p className="text-xs text-muted-foreground">{label}</p>
          {value === undefined ? (
            <Skeleton className="mt-1 h-6 w-8" />
          ) : (
            <p className="text-xl font-semibold">{value}</p>
          )}
        </div>
      </CardContent>
    </Card>
  );
}

function EmptyState({
  message,
  ctaHref,
  ctaLabel,
  icon: Icon,
}: {
  message: string;
  ctaHref?: string;
  ctaLabel?: string;
  icon?: React.ComponentType<{ className?: string }>;
}) {
  return (
    <div className="flex flex-col items-center justify-center gap-3 py-8 text-center">
      {Icon && <Icon className="h-8 w-8 text-muted-foreground" />}
      <p className="text-sm text-muted-foreground">{message}</p>
      {ctaHref && ctaLabel && (
        <Button size="sm" asChild>
          <Link href={ctaHref}>{ctaLabel}</Link>
        </Button>
      )}
    </div>
  );
}