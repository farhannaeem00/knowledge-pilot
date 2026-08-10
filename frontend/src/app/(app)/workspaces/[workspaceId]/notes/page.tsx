"use client";

import { useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import { Plus, StickyNote } from "lucide-react";
import { useNotes } from "@/hooks/use-notes";
import { NoteCard } from "@/components/notes/note-card";
import { NoteEditorDialog } from "@/components/notes/note-editor-dialog";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import type { Note } from "@/types/api";

export default function NotesPage() {
  const params = useParams<{ workspaceId: string }>();
  const { workspaceId } = params;
  const { data: notes, isLoading } = useNotes(workspaceId);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [editingNote, setEditingNote] = useState<Note | null>(null);

  const openNew = () => {
    setEditingNote(null);
    setDialogOpen(true);
  };
  const openEdit = (note: Note) => {
    setEditingNote(note);
    setDialogOpen(true);
  };

  return (
    <div className="mx-auto max-w-5xl space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm text-muted-foreground">
            <Link href={`/workspaces/${workspaceId}`} className="hover:underline">
              ← Back to workspace
            </Link>
          </p>
          <h1 className="text-xl font-bold">Notes</h1>
        </div>
        <Button size="sm" onClick={openNew}>
          <Plus className="mr-1 h-3.5 w-3.5" />
          New Note
        </Button>
      </div>

      {isLoading ? (
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
          <Skeleton className="h-32 w-full" />
          <Skeleton className="h-32 w-full" />
        </div>
      ) : notes && notes.length > 0 ? (
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {notes.map((note) => (
            <NoteCard key={note.id} workspaceId={workspaceId} note={note} onEdit={openEdit} />
          ))}
        </div>
      ) : (
        <div className="flex flex-col items-center justify-center gap-3 rounded-lg border border-dashed border-border py-16 text-center">
          <StickyNote className="h-8 w-8 text-muted-foreground" />
          <p className="text-muted-foreground">No notes yet.</p>
          <Button size="sm" onClick={openNew}>
            Create your first note
          </Button>
        </div>
      )}

      <NoteEditorDialog
        workspaceId={workspaceId}
        open={dialogOpen}
        onOpenChange={setDialogOpen}
        editingNote={editingNote}
      />
    </div>
  );
}