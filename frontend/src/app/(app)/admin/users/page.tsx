"use client";

import Link from "next/link";
import { formatDistanceToNow } from "date-fns";
import { useAdminUsers } from "@/hooks/use-admin";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";

export default function AdminUsersPage() {
  const { data: users, isLoading } = useAdminUsers();

  return (
    <div className="mx-auto max-w-4xl space-y-6">
      <div>
        <p className="text-sm text-muted-foreground">
          <Link href="/admin" className="hover:underline">
            ← Back to admin
          </Link>
        </p>
        <h1 className="text-xl font-bold">Users</h1>
      </div>

      {isLoading ? (
        <div className="space-y-2">
          <Skeleton className="h-14 w-full" />
          <Skeleton className="h-14 w-full" />
        </div>
      ) : (
        <Card>
          <CardContent className="divide-y divide-border p-0">
            {users?.map((user) => (
              <div key={user.id} className="flex items-center justify-between px-4 py-3 text-sm">
                <div>
                  <p className="font-medium">{user.full_name ?? user.email}</p>
                  <p className="text-xs text-muted-foreground">{user.email}</p>
                </div>
                <div className="flex items-center gap-2">
                  {user.role === "admin" && <Badge>Admin</Badge>}
                  <Badge variant={user.is_active ? "secondary" : "destructive"}>
                    {user.is_active ? "Active" : "Inactive"}
                  </Badge>
                  <span className="text-xs text-muted-foreground">
                    Joined {formatDistanceToNow(new Date(user.created_at), { addSuffix: true })}
                  </span>
                </div>
              </div>
            ))}
          </CardContent>
        </Card>
      )}
    </div>
  );
}