"use client";

import { useRef, useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import { FileText, Upload, MessageSquare, StickyNote, Video, Loader2, Layers, Star } from "lucide-react";
import { useWorkspaces } from "@/hooks/use-workspaces";
import { useDocuments, useUploadDocument } from "@/hooks/use-documents";
import { useFolders } from "@/hooks/use-folders";
import { FolderSidebar } from "@/components/workspaces/folder-sidebar";
import { apiClient } from "@/lib/api-client";
import { useQueryClient } from "@tanstack/react-query";

import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { Button } from "@/components/ui/button";
const TABS = [
  { key: "documents", label: "Documents", icon: FileText },
  { key: "collections", label: "Collections", icon: Layers },
  { key: "chat", label: "Chat", icon: MessageSquare },
  { key: "notes", label: "Notes", icon: StickyNote },
  { key: "scripts", label: "Scripts", icon: Video },
] as const;

type TabKey = (typeof TABS)[number]["key"];

const statusColor: Record<string, string> = {
  done: "bg-green-100 text-green-700 border-green-200",
  processing: "bg-blue-100 text-blue-700 border-blue-200",
  uploaded: "bg-blue-100 text-blue-700 border-blue-200",
  failed: "bg-red-100 text-red-700 border-red-200",
  failed_partial: "bg-amber-100 text-amber-700 border-amber-200",
};

export default function WorkspaceDetailPage() {
  const params = useParams<{ workspaceId: string }>();
  const workspaceId = params.workspaceId;
  const [activeTab, setActiveTab] = useState<TabKey>("documents");

  const { data: workspaces } = useWorkspaces();
  const workspace = workspaces?.find((w) => w.id === workspaceId);

  return (
    <div className="mx-auto max-w-5xl space-y-6">
      <div>
        <h1 className="text-2xl font-bold">{workspace?.name ?? "Workspace"}</h1>
        <p className="text-muted-foreground">Documents, chat, notes, and scripts for this workspace.</p>
      </div>

      <div className="flex gap-1 border-b border-border">
        {TABS.map((tab) => {
          const Icon = tab.icon;
          const isActive = activeTab === tab.key;
          return (
            <button
              key={tab.key}
              onClick={() => setActiveTab(tab.key)}
              className={`flex items-center gap-2 border-b-2 px-4 py-2 text-sm font-medium transition-colors ${
                isActive
                  ? "border-primary text-primary"
                  : "border-transparent text-muted-foreground hover:text-foreground"
              }`}
            >
              <Icon className="h-4 w-4" />
              {tab.label}
            </button>
          );
        })}
      </div>

      {activeTab === "documents" && <DocumentsTab workspaceId={workspaceId} />}
      {activeTab === "collections" && <CollectionsLinkTab workspaceId={workspaceId} />}
      {activeTab === "chat" && <ComingSoonTab label="Chat" />}
      {activeTab === "notes" && <NotesLinkTab workspaceId={workspaceId} />}
      {activeTab === "scripts" && <ComingSoonTab label="Video Scripts" />}
    </div>
  );
}


function DocumentsTab({ workspaceId }: { workspaceId: string }) {
  const [activeFolderId, setActiveFolderId] = useState<string | null>(null);
  const { data: documents, isLoading } = useDocuments(workspaceId);
  const { data: folders } = useFolders(workspaceId);
  const uploadDocument = useUploadDocument(workspaceId);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const queryClient = useQueryClient();

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      uploadDocument.mutate(file);
    }
    e.target.value = "";
  };

  const toggleFavorite = async (docId: string, current: boolean) => {
    await apiClient.patch(`/workspaces/${workspaceId}/documents/${docId}`, { is_favorite: !current });
    queryClient.invalidateQueries({ queryKey: ["documents", workspaceId] });
  };

  const assignFolder = async (docId: string, folderId: string | null) => {
    await apiClient.patch(`/workspaces/${workspaceId}/documents/${docId}`, { folder_id: folderId });
    queryClient.invalidateQueries({ queryKey: ["documents", workspaceId] });
  };

  const filteredDocuments = activeFolderId
    ? documents?.filter((d) => d.folder_id === activeFolderId)
    : documents;

  return (
    <div className="flex gap-6">
      <FolderSidebar workspaceId={workspaceId} activeFolderId={activeFolderId} onSelectFolder={setActiveFolderId} />

      <div className="flex-1 space-y-4">
        <div className="flex items-center justify-between">
          <p className="text-sm text-muted-foreground">
            {filteredDocuments?.length ?? 0} document{filteredDocuments?.length === 1 ? "" : "s"}
          </p>
          <input
            ref={fileInputRef}
            type="file"
            accept=".pdf,.docx,.txt,.md"
            className="hidden"
            onChange={handleFileChange}
          />
          <Button size="sm" onClick={() => fileInputRef.current?.click()} disabled={uploadDocument.isPending}>
            {uploadDocument.isPending ? (
              <Loader2 className="mr-1 h-3.5 w-3.5 animate-spin" />
            ) : (
              <Upload className="mr-1 h-3.5 w-3.5" />
            )}
            {uploadDocument.isPending ? "Uploading..." : "Upload Document"}
          </Button>
        </div>

        {uploadDocument.isError && (
          <p className="text-sm text-destructive">
            Upload failed. Supported types: PDF, DOCX, TXT, MD (max 100MB).
          </p>
        )}

        {isLoading ? (
          <div className="space-y-2">
            <Skeleton className="h-16 w-full" />
            <Skeleton className="h-16 w-full" />
          </div>
        ) : filteredDocuments && filteredDocuments.length > 0 ? (
          <div className="space-y-2">
            {filteredDocuments.map((doc) => (
              <Card key={doc.id} className="transition-colors hover:border-primary">
                <CardContent className="flex items-center justify-between p-4">
                  <Link href={`/workspaces/${workspaceId}/documents/${doc.id}`} className="flex flex-1 items-center gap-3 min-w-0">
                    <FileText className="h-5 w-5 shrink-0 text-muted-foreground" />
                    <div className="min-w-0">
                      <p className="truncate font-medium">{doc.title}</p>
                      <p className="text-xs uppercase text-muted-foreground">{doc.source_type}</p>
                    </div>
                  </Link>
                  <div className="flex shrink-0 items-center gap-2">
                    <button onClick={() => toggleFavorite(doc.id, doc.is_favorite)}>
                      <Star className={`h-4 w-4 ${doc.is_favorite ? "fill-amber-400 text-amber-400" : "text-muted-foreground"}`} />
                    </button>
                    <select
                      value={doc.folder_id ?? ""}
                      onChange={(e) => assignFolder(doc.id, e.target.value || null)}
                      onClick={(e) => e.stopPropagation()}
                      className="h-7 rounded-md border border-input bg-transparent px-1.5 text-xs"
                    >
                      <option value="">No folder</option>
                      {folders?.map((f) => (
                        <option key={f.id} value={f.id}>
                          {f.name}
                        </option>
                      ))}
                    </select>
                    <Badge variant="outline" className={statusColor[doc.status] ?? ""}>
                      {doc.status}
                    </Badge>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        ) : (
          <div className="flex flex-col items-center justify-center gap-2 rounded-lg border border-dashed border-border py-12 text-center">
            <FileText className="h-8 w-8 text-muted-foreground" />
            <p className="text-sm text-muted-foreground">
              {activeFolderId ? "No documents in this folder." : "No documents yet. Upload one to get started."}
            </p>
          </div>
        )}
      </div>
    </div>
  );
}

function CollectionsLinkTab({ workspaceId }: { workspaceId: string }) {
  return (
    <div className="flex flex-col items-center justify-center gap-3 rounded-lg border border-dashed border-border py-16 text-center">
      <p className="text-muted-foreground">Group documents into collections that span folders.</p>
      <Link href={`/workspaces/${workspaceId}/collections`}>
        <Button size="sm">Go to Collections</Button>
      </Link>
    </div>
  );
}

function ComingSoonTab({ label }: { label: string }) {
  return (
    <div className="flex flex-col items-center justify-center gap-2 rounded-lg border border-dashed border-border py-16 text-center">
      <p className="text-muted-foreground">{label} is coming in a later step.</p>
    </div>
  );
}
function NotesLinkTab({ workspaceId }: { workspaceId: string }) {
  return (
    <div className="flex flex-col items-center justify-center gap-3 rounded-lg border border-dashed border-border py-16 text-center">
      <p className="text-muted-foreground">Notes are workspace-wide, not tied to one document.</p>
      <Link href={`/workspaces/${workspaceId}/notes`}>
        <Button size="sm">Go to Notes</Button>
      </Link>
    </div>
  );
}