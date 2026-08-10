"use client";

import { useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import { formatDistanceToNow } from "date-fns";
import { FileText, MessageSquare, Sparkles, Video, History, AlertCircle, Trash2, Highlighter } from "lucide-react";
import { useDocument } from "@/hooks/use-documents";
import { useHighlights, useCreateHighlight, useDeleteHighlight } from "@/hooks/use-highlights";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Skeleton } from "@/components/ui/skeleton";
import { VersionStatusBadge } from "@/components/documents/version-badge";
import { UploadNewVersionButton } from "@/components/documents/upload-new-version-button";


function formatBytes(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

export default function DocumentDetailPage() {
  const params = useParams<{ workspaceId: string; documentId: string }>();
  const { workspaceId, documentId } = params;
  const { data: document, isLoading, isError } = useDocument(workspaceId, documentId);

  if (isLoading) {
    return (
      <div className="mx-auto max-w-4xl space-y-4">
        <Skeleton className="h-8 w-64" />
        <Skeleton className="h-32 w-full" />
        <Skeleton className="h-48 w-full" />
      </div>
    );
  }

  if (isError || !document) {
    return <p className="text-sm text-destructive">Failed to load document.</p>;
  }

  const currentVersion = document.versions.find((v) => v.is_current);
  const isReady = currentVersion?.status === "done";
  const otherVersions = document.versions.filter((v) => !v.is_current);

  return (
    <div className="mx-auto max-w-4xl space-y-6">
      <div className="flex items-start justify-between">
        <div>
          <div className="flex items-center gap-2">
            <FileText className="h-5 w-5 text-muted-foreground" />
            <h1 className="text-xl font-bold">{document.title}</h1>
          </div>
          <p className="mt-1 text-sm text-muted-foreground">
            <Link href={`/workspaces/${workspaceId}`} className="hover:underline">
              ← Back to workspace
            </Link>
          </p>
        </div>
        {currentVersion && <UploadNewVersionButton workspaceId={workspaceId} documentId={documentId} />}
      </div>

      {currentVersion && (
        <Card>
          <CardContent className="flex flex-wrap items-center gap-4 p-4 text-sm">
            <VersionStatusBadge status={currentVersion.status} />
            <span className="text-muted-foreground">
              v{currentVersion.version_number} · {formatBytes(currentVersion.size_bytes)}
              {currentVersion.chunk_count !== null && ` · ${currentVersion.chunk_count} chunks`}
            </span>
            <span className="text-muted-foreground">
              Uploaded {formatDistanceToNow(new Date(currentVersion.created_at), { addSuffix: true })}
            </span>
          </CardContent>
        </Card>
      )}

      {currentVersion?.status === "failed" && currentVersion.error_message && (
        <Card className="border-destructive/50 bg-destructive/5">
          <CardContent className="flex items-start gap-2 p-4 text-sm">
            <AlertCircle className="mt-0.5 h-4 w-4 shrink-0 text-destructive" />
            <div>
              <p className="font-medium text-destructive">Processing failed</p>
              <p className="text-muted-foreground">{currentVersion.error_message}</p>
            </div>
          </CardContent>
        </Card>
      )}

      {currentVersion?.status === "failed_partial" && currentVersion.error_message && (
        <Card className="border-amber-300 bg-amber-50">
          <CardContent className="flex items-start gap-2 p-4 text-sm">
            <AlertCircle className="mt-0.5 h-4 w-4 shrink-0 text-amber-600" />
            <div>
              <p className="font-medium text-amber-700">Partially processed</p>
              <p className="text-muted-foreground">{currentVersion.error_message}</p>
            </div>
          </CardContent>
        </Card>
      )}

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
        <ActionCard
          icon={Sparkles}
          title="Summary"
          description="Structured, multi-style AI summary"
          href={`/workspaces/${workspaceId}/documents/${documentId}/summary`}
          disabled={!isReady}
        />
        <ActionCard
          icon={MessageSquare}
          title="Chat"
          description="Ask questions grounded in this document"
          href={`/workspaces/${workspaceId}/documents/${documentId}/chat`}
          disabled={!isReady}
        />
        <ActionCard
          icon={Video}
          title="Video Script"
          description="Generate a script for YouTube, TikTok, and more"
          href={`/workspaces/${workspaceId}/documents/${documentId}/scripts`}
          disabled={!isReady}
        />
      </div>

      {otherVersions.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-base">
              <History className="h-4 w-4" />
              Version History
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-2">
            {otherVersions.map((v) => (
              <div key={v.id} className="flex items-center justify-between rounded-md border border-border px-3 py-2 text-sm">
                <span>
                  v{v.version_number} · {formatBytes(v.size_bytes)}
                </span>
                <div className="flex items-center gap-2">
                  <VersionStatusBadge status={v.status} />
                  <span className="text-xs text-muted-foreground">
                    {formatDistanceToNow(new Date(v.created_at), { addSuffix: true })}
                  </span>
                </div>
              </div>
            ))}
          </CardContent>
        </Card>
      )}

      <HighlightsSection workspaceId={workspaceId} documentId={documentId} />
    </div>
  );
}

function ActionCard({
  icon: Icon,
  title,
  description,
  href,
  disabled,
}: {
  icon: React.ComponentType<{ className?: string }>;
  title: string;
  description: string;
  href: string;
  disabled: boolean;
}) {
  const content = (
    <Card className={disabled ? "opacity-50" : "transition-colors hover:border-primary"}>
      <CardContent className="flex flex-col gap-2 p-4">
        <Icon className="h-5 w-5 text-primary" />
        <p className="font-medium">{title}</p>
        <p className="text-xs text-muted-foreground">{description}</p>
        {disabled && <p className="text-xs text-amber-600">Waiting for processing to finish</p>}
      </CardContent>
    </Card>
  );

  if (disabled) return content;
  return <Link href={href}>{content}</Link>;
}

const LEVEL_STYLES: Record<string, string> = {
  must_read: "bg-red-100 text-red-700 border-red-200",
  important: "bg-amber-100 text-amber-700 border-amber-200",
  optional: "bg-blue-100 text-blue-700 border-blue-200",
  custom: "bg-purple-100 text-purple-700 border-purple-200",
};

function HighlightsSection({ workspaceId, documentId }: { workspaceId: string; documentId: string }) {
  const { data: highlights, isLoading } = useHighlights(workspaceId, documentId);
  const createHighlight = useCreateHighlight(workspaceId, documentId);
  const deleteHighlight = useDeleteHighlight(workspaceId, documentId);

  const [text, setText] = useState("");
  const [level, setLevel] = useState<"must_read" | "important" | "optional" | "custom">("important");
  const [note, setNote] = useState("");

  const handleAdd = () => {
    if (!text.trim()) return;
    createHighlight.mutate(
      {
        level,
        start_offset: 0,
        end_offset: text.length,
        highlighted_text: text.trim(),
        note: note.trim() || null,
      },
      {
        onSuccess: () => {
          setText("");
          setNote("");
        },
      }
    );
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2 text-base">
          <Highlighter className="h-4 w-4" />
          Highlights
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="space-y-2 rounded-md border border-dashed border-border p-3">
          <Textarea
            value={text}
            onChange={(e) => setText(e.target.value)}
            placeholder="Paste or type the text you want to highlight..."
            rows={2}
          />
          <div className="flex flex-wrap items-center gap-2">
            <select
              value={level}
              onChange={(e) => setLevel(e.target.value as typeof level)}
              className="h-9 rounded-md border border-input bg-transparent px-2 text-sm"
            >
              <option value="must_read">Must Read</option>
              <option value="important">Important</option>
              <option value="optional">Optional</option>
              <option value="custom">Custom</option>
            </select>
            <input
              value={note}
              onChange={(e) => setNote(e.target.value)}
              placeholder="Optional note"
              className="h-9 flex-1 rounded-md border border-input bg-transparent px-2 text-sm"
            />
            <Button size="sm" onClick={handleAdd} disabled={createHighlight.isPending || !text.trim()}>
              Add Highlight
            </Button>
          </div>
        </div>

        {isLoading ? (
          <Skeleton className="h-12 w-full" />
        ) : highlights && highlights.length > 0 ? (
          <div className="space-y-2">
            {highlights.map((h) => (
              <div key={h.id} className="flex items-start justify-between gap-2 rounded-md border border-border p-3 text-sm">
                <div className="min-w-0 flex-1">
                  <span className={`mb-1 inline-block rounded border px-1.5 py-0.5 text-xs capitalize ${LEVEL_STYLES[h.level] ?? ""}`}>
                    {h.level.replace("_", " ")}
                  </span>
                  <p className="italic">&quot;{h.highlighted_text}&quot;</p>
                  {h.note && <p className="mt-1 text-muted-foreground">{h.note}</p>}
                </div>
                <Button
                  size="icon"
                  variant="ghost"
                  className="h-7 w-7 shrink-0"
                  onClick={() => deleteHighlight.mutate(h.id)}
                >
                  <Trash2 className="h-3.5 w-3.5" />
                </Button>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-center text-sm text-muted-foreground">No highlights yet.</p>
        )}
      </CardContent>
    </Card>
  );
}
