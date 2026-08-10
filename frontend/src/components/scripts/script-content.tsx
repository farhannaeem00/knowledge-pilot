import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Clock } from "lucide-react";
import type { ScriptContent as ScriptContentType } from "@/types/api";

function formatDuration(seconds: number): string {
  const minutes = Math.floor(seconds / 60);
  const remaining = seconds % 60;
  return `${minutes}:${remaining.toString().padStart(2, "0")}`;
}

export function ScriptContentView({ content }: { content: ScriptContentType }) {
  return (
    <div className="space-y-4">
      <Badge variant="secondary" className="gap-1">
        <Clock className="h-3 w-3" />
        ~{formatDuration(content.estimated_duration_seconds)} estimated
      </Badge>

      <Card>
        <CardHeader>
          <CardTitle className="text-base">Hook</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm font-medium italic">&quot;{content.hook}&quot;</p>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="text-base">Introduction</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm">{content.introduction}</p>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="text-base">Body</CardTitle>
        </CardHeader>
        <CardContent>
          <ol className="list-decimal space-y-2 pl-5 text-sm">
            {content.body.map((point, i) => (
              <li key={i}>{point}</li>
            ))}
          </ol>
        </CardContent>
      </Card>

      {content.examples.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Examples</CardTitle>
          </CardHeader>
          <CardContent>
            <ul className="list-disc space-y-1.5 pl-5 text-sm">
              {content.examples.map((example, i) => (
                <li key={i}>{example}</li>
              ))}
            </ul>
          </CardContent>
        </Card>
      )}

      <Card>
        <CardHeader>
          <CardTitle className="text-base">Call to Action</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm">{content.cta}</p>
        </CardContent>
      </Card>
    </div>
  );
}