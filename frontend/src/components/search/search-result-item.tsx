import Link from "next/link";
import { FileText, StickyNote, Sparkles } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import type { SearchResult } from "@/hooks/use-search";

const TYPE_CONFIG = {
  document_chunk: { icon: FileText, label: "Document" },
  note: { icon: StickyNote, label: "Note" },
  summary: { icon: Sparkles, label: "Summary" },
} as const;

function resultHref(result: SearchResult): string {
  if (result.result_type === "note") {
    return `/workspaces/${result.workspace_id}/notes`;
  }
  if (result.result_type === "summary") {
    return `/workspaces/${result.workspace_id}/documents/${result.document_id}/summary`;
  }
  return `/workspaces/${result.workspace_id}/documents/${result.document_id}`;
}

export function SearchResultItem({ result }: { result: SearchResult }) {
  const config = TYPE_CONFIG[result.result_type];
  const Icon = config.icon;

  return (
    <Link href={resultHref(result)}>
      <Card className="transition-colors hover:border-primary">
        <CardContent className="flex items-start gap-3 p-4">
          <div className="rounded-md bg-primary/10 p-2">
            <Icon className="h-4 w-4 text-primary" />
          </div>
          <div className="min-w-0 flex-1">
            <div className="flex items-center gap-2">
              <p className="truncate font-medium">{result.title}</p>
              <Badge variant="secondary" className="shrink-0 text-xs">
                {config.label}
              </Badge>
            </div>
            <p className="mt-1 line-clamp-2 text-sm text-muted-foreground">{result.snippet}</p>
          </div>
          <span className="shrink-0 text-xs text-muted-foreground">{Math.round(result.score * 100)}%</span>
        </CardContent>
      </Card>
    </Link>
  );
}