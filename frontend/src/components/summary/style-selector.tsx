"use client";

import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import type { SummaryStyle } from "@/hooks/use-summary";

const STYLE_LABELS: Record<SummaryStyle, string> = {
  executive: "Executive",
  beginner: "Beginner Friendly",
  technical: "Technical",
  bullet_points: "Bullet Points",
  detailed: "Detailed",
  academic: "Academic",
  content_creator: "Content Creator",
};

export function StyleSelector({
  value,
  onChange,
}: {
  value: SummaryStyle;
  onChange: (style: SummaryStyle) => void;
}) {
  return (
    <Select value={value} onValueChange={(v) => onChange(v as SummaryStyle)}>
      <SelectTrigger className="w-56">
        <SelectValue />
      </SelectTrigger>
      <SelectContent>
        {(Object.keys(STYLE_LABELS) as SummaryStyle[]).map((style) => (
          <SelectItem key={style} value={style}>
            {STYLE_LABELS[style]}
          </SelectItem>
        ))}
      </SelectContent>
    </Select>
  );
}