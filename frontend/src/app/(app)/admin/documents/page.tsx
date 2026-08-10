"use client";

import Link from "next/link";
import { formatDistanceToNow } from "date-fns";
import { useAdminDocuments } from "@/hooks/use-admin";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";

const statusColor: Record<string, string> = {
  active: "bg-green-100 text-green-700 border-green-200",
  archived: "bg-gray-100 text-gray-700 border-gray-200",
  trashed: "bg-red-100 text-red-700 border-red-200",
};

export default function AdminDocumentsPage() {
  const { data: documents, isLoading } = useAdminDocuments();

  return (
    <div className="mx-auto max-w-4xl space-y-6">
      <div>
        <p className="text-sm text-muted-foreground">
          <Link href="/admin" className="hover:underline">
            ← Back to admin
          </Link>
        </p>
        <h1 className="text-xl font-bold">Documents</h1>
      </div>

      {isLoading ? (
        <div className="space-y-2">
          <Skeleton className="h-14 w-full" />
          <Skeleton className="h-14 w-full" />
        </div>
      ) : (
        <Card>
          <CardContent className="divide-y divide-border p-0">
            {documents?.map((doc) => (
              <div key={doc.id} className="flex items-center justify-between px-4 py-3 text-sm">
                <div>
                  <p className="font-medium">{doc.title}</p>
                  <p className="text-xs uppercase text-muted-foreground">{doc.source_type}</p>
                </div>
                <div className="flex items-center gap-2">
                  <Badge variant="outline" className={statusColor[doc.status] ?? ""}>
                    {doc.status}
                  </Badge>
                  <span className="text-xs text-muted-foreground">
                    {formatDistanceToNow(new Date(doc.created_at), { addSuffix: true })}
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