"use client";

import Link from "next/link";
import { Bell } from "lucide-react";
import { useUnreadCount } from "@/hooks/use-notifications";

export function NotificationBell() {
  const { data } = useUnreadCount();
  const count = data?.unread_count ?? 0;

  return (
    <Link href="/notifications" className="relative rounded-full p-2 hover:bg-accent">
      <Bell className="h-5 w-5 text-muted-foreground" />
      {count > 0 && (
        <span className="absolute right-1 top-1 flex h-4 min-w-4 items-center justify-center rounded-full bg-destructive px-1 text-[10px] font-medium text-destructive-foreground">
          {count > 9 ? "9+" : count}
        </span>
      )}
    </Link>
  );
}