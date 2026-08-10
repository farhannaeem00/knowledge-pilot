"use client";

import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import type { ScriptPlatform } from "@/hooks/use-scripts";

const PLATFORM_LABELS: Record<ScriptPlatform, string> = {
  youtube: "YouTube",
  linkedin: "LinkedIn",
  instagram_reel: "Instagram Reel",
  tiktok: "TikTok",
  podcast: "Podcast",
  presentation: "Presentation",
};

export function PlatformSelector({
  value,
  onChange,
}: {
  value: ScriptPlatform;
  onChange: (platform: ScriptPlatform) => void;
}) {
  return (
    <Select value={value} onValueChange={(v) => onChange(v as ScriptPlatform)}>
      <SelectTrigger className="w-48">
        <SelectValue />
      </SelectTrigger>
      <SelectContent>
        {(Object.keys(PLATFORM_LABELS) as ScriptPlatform[]).map((platform) => (
          <SelectItem key={platform} value={platform}>
            {PLATFORM_LABELS[platform]}
          </SelectItem>
        ))}
      </SelectContent>
    </Select>
  );
}   