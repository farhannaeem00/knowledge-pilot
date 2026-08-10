"use client";

import { Pin, Trash2 } from "lucide-react";
import { formatDistanceToNow } from "date-fns";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { useUpdateNote, useDeleteNote } from "@/hooks/use-notes";
import type { Note } from "@/types/api";

export function NoteCard({
  workspaceId,
  note,
  onEdit,
}: {
  workspaceId: string;
  note: Note;
  onEdit: (note: Note) => void;
}) {
  const updateNote = useUpdateNote(workspaceId);
  const deleteNote = useDeleteNote(workspaceId);

  return (
    <Card className="transition-colors hover:border-primary">
      <CardContent className="space-y-2 p-4">
        <div className="flex items-start justify-between gap-2">
          <button className="min-w-0 flex-1 text-left" onClick={() => onEdit(note)}>
            <p className="truncate font-medium">{note.title}</p>
          </button>
          <div className="flex shrink-0 items-center gap-1">
            <Button
              size="icon"
              variant="ghost"
              className="h-7 w-7"
              onClick={() => updateNote.mutate({ noteId: note.id, input: { is_pinned: !note.is_pinned } })}
            >
              <Pin className={`h-3.5 w-3.5 ${note.is_pinned ? "fill-primary text-primary" : ""}`} />
            </Button>
            <Button
              size="icon"
              variant="ghost"
              className="h-7 w-7"
              onClick={() => deleteNote.mutate(note.id)}
              disabled={deleteNote.isPending}
            >
              <Trash2 className="h-3.5 w-3.5" />
            </Button>
          </div>
        </div>
        <p className="line-clamp-3 whitespace-pre-wrap text-sm text-muted-foreground">
          {note.content_md || "No content"}
        </p>
        <div className="flex flex-wrap items-center gap-1.5">
          {note.tags?.map((tag) => (
            <Badge key={tag} variant="secondary" className="text-xs">
              {tag}
            </Badge>
          ))}
        </div>
        <p className="text-xs text-muted-foreground">
          Updated {formatDistanceToNow(new Date(note.updated_at), { addSuffix: true })}
        </p>
      </CardContent>
    </Card>
  );
}