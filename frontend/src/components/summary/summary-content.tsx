import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Clock, Gauge, ShieldCheck } from "lucide-react";
import type { SummaryContent as SummaryContentType } from "@/types/api";

function BulletList({ items }: { items: string[] }) {
  if (items.length === 0) return <p className="text-sm text-muted-foreground">None identified.</p>;
  return (
    <ul className="list-disc space-y-1.5 pl-5 text-sm">
      {items.map((item, i) => (
        <li key={i}>{item}</li>
      ))}
    </ul>
  );
}

export function SummaryContentView({ content }: { content: SummaryContentType }) {
  return (
    <div className="space-y-6">
      <div className="flex flex-wrap gap-3">
        <Badge variant="secondary" className="gap-1">
          <Clock className="h-3 w-3" />
          {content.reading_time_minutes} min read
        </Badge>
        <Badge variant="secondary" className="gap-1 capitalize">
          <Gauge className="h-3 w-3" />
          {content.difficulty_level}
        </Badge>
        <Badge variant="secondary" className="gap-1">
          <ShieldCheck className="h-3 w-3" />
          {Math.round(content.confidence_score * 100)}% confidence
        </Badge>
      </div>

      <Tabs defaultValue="overview">
        <TabsList>
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="key-points">Key Points</TabsTrigger>
          <TabsTrigger value="sections">Sections</TabsTrigger>
          <TabsTrigger value="pros-cons">Pros & Cons</TabsTrigger>
          <TabsTrigger value="takeaways">Takeaways</TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="text-base">Overview</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm">{content.overview}</p>
            </CardContent>
          </Card>
          <Card>
            <CardHeader>
              <CardTitle className="text-base">Executive Summary</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm">{content.executive_summary}</p>
            </CardContent>
          </Card>
          <Card>
            <CardHeader>
              <CardTitle className="text-base">Conclusion</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm">{content.conclusion}</p>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="key-points" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="text-base">Key Ideas</CardTitle>
            </CardHeader>
            <CardContent>
              <BulletList items={content.key_ideas} />
            </CardContent>
          </Card>
          <Card>
            <CardHeader>
              <CardTitle className="text-base">Important Concepts</CardTitle>
            </CardHeader>
            <CardContent>
              <BulletList items={content.important_concepts} />
            </CardContent>
          </Card>
          <Card>
            <CardHeader>
              <CardTitle className="text-base">Important Statistics</CardTitle>
            </CardHeader>
            <CardContent>
              <BulletList items={content.important_statistics} />
            </CardContent>
          </Card>
          <Card>
            <CardHeader>
              <CardTitle className="text-base">Examples</CardTitle>
            </CardHeader>
            <CardContent>
              <BulletList items={content.examples} />
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="sections" className="space-y-4">
          {content.section_summary.length === 0 ? (
            <p className="text-sm text-muted-foreground">No section breakdown available.</p>
          ) : (
            content.section_summary.map((section, i) => (
              <Card key={i}>
                <CardHeader>
                  <CardTitle className="text-base">{section.title}</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-sm">{section.summary}</p>
                </CardContent>
              </Card>
            ))
          )}
        </TabsContent>

        <TabsContent value="pros-cons" className="grid grid-cols-1 gap-4 sm:grid-cols-2">
          <Card>
            <CardHeader>
              <CardTitle className="text-base text-green-700">Pros</CardTitle>
            </CardHeader>
            <CardContent>
              <BulletList items={content.pros} />
            </CardContent>
          </Card>
          <Card>
            <CardHeader>
              <CardTitle className="text-base text-red-700">Cons</CardTitle>
            </CardHeader>
            <CardContent>
              <BulletList items={content.cons} />
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="takeaways" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="text-base">Actionable Insights</CardTitle>
            </CardHeader>
            <CardContent>
              <BulletList items={content.actionable_insights} />
            </CardContent>
          </Card>
          <Card>
            <CardHeader>
              <CardTitle className="text-base">Key Takeaways</CardTitle>
            </CardHeader>
            <CardContent>
              <BulletList items={content.key_takeaways} />
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}