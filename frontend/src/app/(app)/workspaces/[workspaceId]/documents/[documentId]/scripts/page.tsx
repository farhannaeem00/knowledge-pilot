"use client";

import { useMemo, useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import { Video, Loader2, RotateCcw, AlertCircle } from "lucide-react";
import { useScripts, useGenerateScript, type ScriptPlatform } from "@/hooks/use-scripts";
import { PlatformSelector } from "@/components/scripts/platform-selector";
import { ScriptContentView } from "@/components/scripts/script-content";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";

export default function ScriptsPage() {
  const params = useParams<{ workspaceId: string; documentId: string }>();
  const { workspaceId, documentId } = params;
  const [platform, setPlatform] = useState<ScriptPlatform>("youtube");

  const { data: scripts, isLoading } = useScripts(workspaceId, documentId);
  const generateScript = useGenerateScript(workspaceId, documentId);

  const scriptsForPlatform = useMemo(
    () => (scripts ?? []).filter((s) => s.platform === platform).sort((a, b) => b.created_at.localeCompare(a.created_at)),
    [scripts, platform]
  );
  const latest = scriptsForPlatform[0];
  const isGenerating = latest?.status === "pending" || latest?.status === "processing";

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
            <Video className="h-5 w-5 text-primary" />
            Video Script
          </h1>
          <PlatformSelector value={platform} onChange={setPlatform} />
        </div>
      </div>

      {isLoading && (
        <div className="space-y-3">
          <Skeleton className="h-6 w-48" />
          <Skeleton className="h-32 w-full" />
        </div>
      )}

      {!isLoading && !latest && (
        <div className="flex flex-col items-center justify-center gap-3 rounded-lg border border-dashed border-border py-16 text-center">
          <Video className="h-8 w-8 text-muted-foreground" />
          <p className="text-muted-foreground">No script generated for this platform yet.</p>
          <Button onClick={() => generateScript.mutate(platform)} disabled={generateScript.isPending}>
            Generate Script
          </Button>
        </div>
      )}

      {isGenerating && (
        <div className="flex flex-col items-center justify-center gap-3 rounded-lg border border-border py-16 text-center">
          <Loader2 className="h-8 w-8 animate-spin text-primary" />
          <p className="text-muted-foreground">Generating script...</p>
        </div>
      )}

      {latest?.status === "failed" && (
        <div className="flex flex-col items-center gap-3 rounded-lg border border-destructive/50 bg-destructive/5 py-10 text-center">
          <AlertCircle className="h-8 w-8 text-destructive" />
          <p className="text-sm text-destructive">{latest.error_message ?? "Script generation failed."}</p>
          <Button variant="outline" onClick={() => generateScript.mutate(platform)}>
            <RotateCcw className="mr-1 h-3.5 w-3.5" />
            Try Again
          </Button>
        </div>
      )}

      {latest?.status === "done" && latest.content_json && (
        <div className="space-y-4">
          <div className="flex items-center justify-end">
            <Button size="sm" variant="outline" onClick={() => generateScript.mutate(platform)} disabled={generateScript.isPending}>
              <RotateCcw className="mr-1 h-3.5 w-3.5" />
              Generate New Version
            </Button>
          </div>
          <ScriptContentView content={latest.content_json} />
        </div>
      )}

      {scriptsForPlatform.length > 1 && (
        <div className="border-t border-border pt-4">
          <p className="mb-2 text-xs font-medium text-muted-foreground">
            {scriptsForPlatform.length - 1} earlier version{scriptsForPlatform.length - 1 === 1 ? "" : "s"} for this platform (not shown)
          </p>
        </div>
      )}
    </div>
  );
}