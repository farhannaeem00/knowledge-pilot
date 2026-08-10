"use client";

import Link from "next/link";
import { Users, FileText, HardDrive, Zap } from "lucide-react";
import { useStorageStats, useAIUsageSummary, useAIUsageByFeature } from "@/hooks/use-admin";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { Badge } from "@/components/ui/badge";

function formatBytes(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

export default function AdminPage() {
  const { data: storage, isLoading: storageLoading } = useStorageStats();
  const { data: usage, isLoading: usageLoading } = useAIUsageSummary();
  const { data: byFeature, isLoading: featureLoading } = useAIUsageByFeature();

  return (
    <div className="mx-auto max-w-5xl space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Admin</h1>
        <p className="text-muted-foreground">Platform overview and management.</p>
      </div>

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
        <Link href="/admin/users">
          <Card className="transition-colors hover:border-primary">
            <CardContent className="flex items-center gap-3 p-4">
              <Users className="h-5 w-5 text-primary" />
              <div>
                <p className="font-medium">Users</p>
                <p className="text-xs text-muted-foreground">View all platform users</p>
              </div>
            </CardContent>
          </Card>
        </Link>
        <Link href="/admin/documents">
          <Card className="transition-colors hover:border-primary">
            <CardContent className="flex items-center gap-3 p-4">
              <FileText className="h-5 w-5 text-primary" />
              <div>
                <p className="font-medium">Documents</p>
                <p className="text-xs text-muted-foreground">View all uploaded documents</p>
              </div>
            </CardContent>
          </Card>
        </Link>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-base">
            <HardDrive className="h-4 w-4" />
            Storage
          </CardTitle>
        </CardHeader>
        <CardContent>
          {storageLoading ? (
            <Skeleton className="h-16 w-full" />
          ) : storage ? (
            <div className="grid grid-cols-3 gap-4 text-center">
              <div>
                <p className="text-2xl font-semibold">{storage.total_documents}</p>
                <p className="text-xs text-muted-foreground">Documents</p>
              </div>
              <div>
                <p className="text-2xl font-semibold">{storage.total_versions}</p>
                <p className="text-xs text-muted-foreground">Versions</p>
              </div>
              <div>
                <p className="text-2xl font-semibold">{formatBytes(storage.total_size_bytes)}</p>
                <p className="text-xs text-muted-foreground">Total Size</p>
              </div>
            </div>
          ) : null}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-base">
            <Zap className="h-4 w-4" />
            AI Usage
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {usageLoading ? (
            <Skeleton className="h-16 w-full" />
          ) : usage ? (
            <div className="grid grid-cols-4 gap-4 text-center">
              <div>
                <p className="text-2xl font-semibold">{usage.total_calls}</p>
                <p className="text-xs text-muted-foreground">Total Calls</p>
              </div>
              <div>
                <p className="text-2xl font-semibold">{usage.total_tokens_in.toLocaleString()}</p>
                <p className="text-xs text-muted-foreground">Tokens In</p>
              </div>
              <div>
                <p className="text-2xl font-semibold">{usage.total_tokens_out.toLocaleString()}</p>
                <p className="text-xs text-muted-foreground">Tokens Out</p>
              </div>
              <div>
                <p className="text-2xl font-semibold">{Math.round(usage.avg_latency_ms)}ms</p>
                <p className="text-xs text-muted-foreground">Avg Latency</p>
              </div>
            </div>
          ) : null}

          {featureLoading ? (
            <Skeleton className="h-8 w-full" />
          ) : byFeature && byFeature.length > 0 ? (
            <div className="flex flex-wrap gap-2 border-t border-border pt-4">
              {byFeature.map((f) => (
                <Badge key={f.feature} variant="secondary" className="capitalize">
                  {f.feature}: {f.count}
                </Badge>
              ))}
            </div>
          ) : null}
        </CardContent>
      </Card>
    </div>
  );
}