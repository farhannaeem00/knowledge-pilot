import { Badge } from "@/components/ui/badge";
import { Loader2 } from "lucide-react";

const statusStyles: Record<string, string> = {
  done: "bg-green-100 text-green-700 border-green-200",
  processing: "bg-blue-100 text-blue-700 border-blue-200",
  uploaded: "bg-blue-100 text-blue-700 border-blue-200",
  failed: "bg-red-100 text-red-700 border-red-200",
  failed_partial: "bg-amber-100 text-amber-700 border-amber-200",
};

const statusLabels: Record<string, string> = {
  done: "Ready",
  processing: "Processing",
  uploaded: "Queued",
  failed: "Failed",
  failed_partial: "Partially processed",
};

export function VersionStatusBadge({ status }: { status: string }) {
  const isActive = status === "processing" || status === "uploaded";
  return (
    <Badge variant="outline" className={statusStyles[status] ?? ""}>
      {isActive && <Loader2 className="mr-1 h-3 w-3 animate-spin" />}
      {statusLabels[status] ?? status}
    </Badge>
  );
}