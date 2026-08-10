"use client";

import { useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import { Layers, X, Plus } from "lucide-react";
import { useCollections, useCollectionDocuments, useAddDocumentToCollection, useRemoveDocumentFromCollection } from "@/hooks/use-collections";
import { useDocuments } from "@/hooks/use-documents";
import { CreateCollectionDialog } from "@/components/workspaces/create-collection-dialog";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { cn } from "@/lib/utils";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";

export default function CollectionsPage() {
  const params = useParams<{ workspaceId: string }>();
  const { workspaceId } = params;
  const { data: collections, isLoading } = useCollections(workspaceId);
  const [activeCollectionId, setActiveCollectionId] = useState<string | null>(null);
  const [pickerOpen, setPickerOpen] = useState(false);

  const { data: collectionDocs } = useCollectionDocuments(workspaceId, activeCollectionId);
  const { data: allDocs } = useDocuments(workspaceId);
  const addDoc = useAddDocumentToCollection(workspaceId, activeCollectionId ?? "");
  const removeDoc = useRemoveDocumentFromCollection(workspaceId, activeCollectionId ?? "");

  const activeCollection = collections?.find((c) => c.id === activeCollectionId);
  const collectionDocIds = new Set((collectionDocs ?? []).map((d) => d.id));
  const availableDocs = (allDocs ?? []).filter((d) => !collectionDocIds.has(d.id));

  return (
    <div className="mx-auto max-w-5xl space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm text-muted-foreground">
            <Link href={`/workspaces/${workspaceId}`} className="hover:underline">
              ← Back to workspace
            </Link>
          </p>
          <h1 className="text-xl font-bold">Collections</h1>
        </div>
        <CreateCollectionDialog workspaceId={workspaceId} />
      </div>

      {isLoading ? (
        <Skeleton className="h-24 w-full" />
      ) : collections && collections.length > 0 ? (
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {collections.map((collection) => (
            <Card
              key={collection.id}
              className="cursor-pointer transition-colors hover:border-primary"
              onClick={() => setActiveCollectionId(collection.id)}
            >
              <CardContent className="flex items-center gap-3 p-4">
                <div className="rounded-md bg-primary/10 p-2">
                  <Layers className="h-4 w-4 text-primary" />
                </div>
                <p className="font-medium">{collection.name}</p>
              </CardContent>
            </Card>
          ))}
        </div>
      ) : (
        <div className="flex flex-col items-center justify-center gap-3 rounded-lg border border-dashed border-border py-16 text-center">
          <Layers className="h-8 w-8 text-muted-foreground" />
          <p className="text-muted-foreground">No collections yet. Group documents across folders.</p>
        </div>
      )}

      <Dialog open={!!activeCollectionId} onOpenChange={(open) => !open && setActiveCollectionId(null)}>
        <DialogContent className="max-w-lg">
          <DialogHeader>
            <DialogTitle>{activeCollection?.name}</DialogTitle>
          </DialogHeader>

          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <p className="text-sm font-medium text-muted-foreground">Documents in this collection</p>
              <Button size="sm" variant="outline" onClick={() => setPickerOpen(true)}>
                <Plus className="mr-1 h-3.5 w-3.5" />
                Add
              </Button>
            </div>

            {collectionDocs && collectionDocs.length > 0 ? (
              <div className="space-y-1.5">
                {collectionDocs.map((doc) => (
                  <div key={doc.id} className="flex items-center justify-between rounded-md border border-border px-3 py-2 text-sm">
                    <span className="truncate">{doc.title}</span>
                    <Button
                      size="icon"
                      variant="ghost"
                      className="h-6 w-6 shrink-0"
                      onClick={() => removeDoc.mutate(doc.id)}
                    >
                      <X className="h-3.5 w-3.5" />
                    </Button>
                  </div>
                ))}
              </div>
            ) : (
              <p className="py-6 text-center text-sm text-muted-foreground">No documents added yet.</p>
            )}
          </div>

          {pickerOpen && (
            <div className="space-y-1.5 border-t border-border pt-3">
              <p className="text-sm font-medium text-muted-foreground">Add a document</p>
              {availableDocs.length > 0 ? (
                <div className="max-h-40 space-y-1 overflow-y-auto">
                  {availableDocs.map((doc) => (
                    <button
                      key={doc.id}
                      onClick={() => addDoc.mutate(doc.id)}
                      className={cn(
                        "flex w-full items-center justify-between rounded-md px-3 py-2 text-left text-sm hover:bg-accent"
                      )}
                    >
                      <span className="truncate">{doc.title}</span>
                    </button>
                  ))}
                </div>
              ) : (
                <p className="text-sm text-muted-foreground">All documents are already in this collection.</p>
              )}
            </div>
          )}
        </DialogContent>
      </Dialog>
    </div>
  );
}