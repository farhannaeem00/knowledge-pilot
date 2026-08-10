"use client";

import { useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import { Sparkles, Loader2, RotateCcw, AlertCircle } from "lucide-react";
import { useActiveSummary, useGenerateSummary, type SummaryStyle } from "@/hooks/use-summary";
import { StyleSelector } from "@/components/summary/style-selector";
import { SummaryContentView } from "@/components/summary/summary-content";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { ApiRequestError } from "@/lib/api-client";

export default function SummaryPage() {
  const params = useParams<{ workspaceId: string; documentId: string }>();
  const { workspaceId, documentId } = params;
  const [style, setStyle] = useState<SummaryStyle>("detailed");

  const { data: summary, isLoading, isError, error } = useActiveSummary(workspaceId, documentId, style);
  const generateSummary = useGenerateSummary(workspaceId, documentId);

  const notFound = isError && error instanceof ApiRequestError && error.status === 404;
  const isGenerating = summary?.status === "pending" || summary?.status === "processing";

  return (
    <div className="mx-auto max-w-3xl space-y-6">
      <div>
        <p className="text-sm text-muted-foreground">
          <Link href={`/workspaces/${workspaceId}/documents/${documentId}`} className="hover:underline">
            ← Back to document
          </Link>
        </p>
        <div className="mt-1 flex items-center justify-between gap-4">
          <h1 className="flex items-center gap-2 text-xl font-bold">
            <Sparkles className="h-5 w-5 text-primary" />
            Summary
          </h1>
          <StyleSelector value={style} onChange={setStyle} />
        </div>
      </div>

      {isLoading && (
        <div className="space-y-3">
          <Skeleton className="h-6 w-48" />
          <Skeleton className="h-32 w-full" />
          <Skeleton className="h-32 w-full" />
        </div>
      )}

      {notFound && !generateSummary.isPending && (
        <div className="flex flex-col items-center justify-center gap-3 rounded-lg border border-dashed border-border py-16 text-center">
          <Sparkles className="h-8 w-8 text-muted-foreground" />
          <p className="text-muted-foreground">No {style.replace("_", " ")} summary yet.</p>
          <Button onClick={() => generateSummary.mutate(style)} disabled={generateSummary.isPending}>
            Generate Summary
          </Button>
        </div>
      )}

      {isGenerating && (
        <div className="flex flex-col items-center justify-center gap-3 rounded-lg border border-border py-16 text-center">
          <Loader2 className="h-8 w-8 animate-spin text-primary" />
          <p className="text-muted-foreground">Generating summary...</p>
        </div>
      )}

      {summary?.status === "failed" && (
        <div className="flex flex-col items-center gap-3 rounded-lg border border-destructive/50 bg-destructive/5 py-10 text-center">
          <AlertCircle className="h-8 w-8 text-destructive" />
          <p className="text-sm text-destructive">{summary.error_message ?? "Summary generation failed."}</p>
          <Button variant="outline" onClick={() => generateSummary.mutate(style)}>
            <RotateCcw className="mr-1 h-3.5 w-3.5" />
            Try Again
          </Button>
        </div>
      )}

      {summary?.status === "done" && summary.content_json && (
        <div className="space-y-4">
          <div className="flex items-center justify-end">
            <Button
              size="sm"
              variant="outline"
              onClick={() => generateSummary.mutate(style)}
              disabled={generateSummary.isPending}
            >
              <RotateCcw className="mr-1 h-3.5 w-3.5" />
              Regenerate
            </Button>
          </div>
          <SummaryContentView content={summary.content_json} />
        </div>
      )}
    </div>
  );
}