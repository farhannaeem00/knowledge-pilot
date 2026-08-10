"use client";

import { useRef } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { apiClient } from "@/lib/api-client";
import { Button } from "@/components/ui/button";
import { Upload, Loader2 } from "lucide-react";
import type { DocumentVersion } from "@/types/api";

/**
 * Re-upload flow: creates a new version rather than overwriting (per
 * the versioning decision from requirements review). Separate mutation
 * from the initial-upload one in use-documents.ts since the endpoint
 * differs (/versions suffix, includes documentId).
 */
export function UploadNewVersionButton({ workspaceId, documentId }: { workspaceId: string; documentId: string }) {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const queryClient = useQueryClient();

  const uploadVersion = useMutation({
    mutationFn: (file: File) => {
      const formData = new FormData();
      formData.append("file", file);
      return apiClient.postForm<DocumentVersion>(
        `/workspaces/${workspaceId}/documents/${documentId}/versions`,
        formData
      );
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["document", workspaceId, documentId] });
    },
  });

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) uploadVersion.mutate(file);
    e.target.value = "";
  };

  return (
    <>
      <input ref={fileInputRef} type="file" accept=".pdf,.docx,.txt,.md" className="hidden" onChange={handleFileChange} />
      <Button size="sm" variant="outline" onClick={() => fileInputRef.current?.click()} disabled={uploadVersion.isPending}>
        {uploadVersion.isPending ? <Loader2 className="mr-1 h-3.5 w-3.5 animate-spin" /> : <Upload className="mr-1 h-3.5 w-3.5" />}
        {uploadVersion.isPending ? "Uploading..." : "Upload New Version"}
      </Button>
      {uploadVersion.isError && <p className="mt-2 text-sm text-destructive">Upload failed.</p>}
    </>
  );
}