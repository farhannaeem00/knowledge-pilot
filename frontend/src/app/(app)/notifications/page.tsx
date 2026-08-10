"use client";

import { formatDistanceToNow } from "date-fns";
import { Bell, CheckCircle2, XCircle, Sparkles, Video } from "lucide-react";
import { useNotifications, useMarkNotificationRead, useMarkAllRead } from "@/hooks/use-notifications";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { cn } from "@/lib/utils";
import type { Notification } from "@/types/api";

const TYPE_CONFIG: Record<string, { icon: typeof Bell; label: string; color: string }> = {
  processing_complete: { icon: CheckCircle2, label: "Document processed", color: "text-green-600" },
  processing_failed: { icon: XCircle, label: "Processing failed", color: "text-red-600" },
  summary_ready: { icon: Sparkles, label: "Summary ready", color: "text-primary" },
  script_ready: { icon: Video, label: "Script ready", color: "text-primary" },
};

function describeNotification(n: Notification): string {
  const payload = n.payload as Record<string, string> | null;
  switch (n.type) {
    case "processing_complete":
    case "processing_failed":
      return payload?.document_title ? `"${payload.document_title}"` : "A document";
    case "summary_ready":
      return payload?.document_title
        ? `${payload.style ? `${payload.style} ` : ""}summary for "${payload.document_title}"`
        : "A summary";
    case "script_ready":
      return payload?.platform ? `${payload.platform} script` : "A script";
    default:
      return "";
  }
}

export default function NotificationsPage() {
  const { data: notifications, isLoading } = useNotifications();
  const markRead = useMarkNotificationRead();
  const markAllRead = useMarkAllRead();

  const hasUnread = notifications?.some((n) => !n.read_at);

  return (
    <div className="mx-auto max-w-2xl space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">Notifications</h1>
        {hasUnread && (
          <Button size="sm" variant="outline" onClick={() => markAllRead.mutate()} disabled={markAllRead.isPending}>
            Mark all read
          </Button>
        )}
      </div>

      {isLoading ? (
        <div className="space-y-2">
          <Skeleton className="h-16 w-full" />
          <Skeleton className="h-16 w-full" />
        </div>
      ) : notifications && notifications.length > 0 ? (
        <div className="space-y-2">
          {notifications.map((n) => {
            const config = TYPE_CONFIG[n.type] ?? { icon: Bell, label: n.type, color: "text-muted-foreground" };
            const Icon = config.icon;
            const isUnread = !n.read_at;
            return (
              <Card
                key={n.id}
                className={cn("cursor-pointer transition-colors", isUnread && "border-primary/40 bg-primary/5")}
                onClick={() => isUnread && markRead.mutate(n.id)}
              >
                <CardContent className="flex items-start gap-3 p-4">
                  <Icon className={cn("mt-0.5 h-5 w-5 shrink-0", config.color)} />
                  <div className="min-w-0 flex-1">
                    <p className="text-sm font-medium">{config.label}</p>
                    <p className="text-sm text-muted-foreground">{describeNotification(n)}</p>
                    <p className="mt-1 text-xs text-muted-foreground">
                      {formatDistanceToNow(new Date(n.created_at), { addSuffix: true })}
                    </p>
                  </div>
                  {isUnread && <span className="mt-1 h-2 w-2 shrink-0 rounded-full bg-primary" />}
                </CardContent>
              </Card>
            );
          })}
        </div>
      ) : (
        <div className="flex flex-col items-center justify-center gap-3 rounded-lg border border-dashed border-border py-16 text-center">
          <Bell className="h-8 w-8 text-muted-foreground" />
          <p className="text-muted-foreground">No notifications yet.</p>
        </div>
      )}
    </div>
  );
}