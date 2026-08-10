"use client";

import { useEffect, useState } from "react";
import { Dialog, DialogContent, DialogFooter, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { Button } from "@/components/ui/button";
import { useCreateNote, useUpdateNote } from "@/hooks/use-notes";
import type { Note } from "@/types/api";

export function NoteEditorDialog({
  workspaceId,
  open,
  onOpenChange,
  editingNote,
}: {
  workspaceId: string;
  open: boolean;
  onOpenChange: (open: boolean) => void;
  editingNote: Note | null;
}) {
  const [title, setTitle] = useState("");
  const [content, setContent] = useState("");
  const [tagsInput, setTagsInput] = useState("");

  const createNote = useCreateNote(workspaceId);
  const updateNote = useUpdateNote(workspaceId);
  const isSaving = createNote.isPending || updateNote.isPending;

  useEffect(() => {
    if (open) {
      setTitle(editingNote?.title ?? "");
      setContent(editingNote?.content_md ?? "");
      setTagsInput(editingNote?.tags?.join(", ") ?? "");
    }
  }, [open, editingNote]);

  const handleSave = () => {
    const tags = tagsInput
      .split(",")
      .map((t) => t.trim())
      .filter(Boolean);

    if (editingNote) {
      updateNote.mutate(
        { noteId: editingNote.id, input: { title: title || "Untitled Note", content_md: content, tags } },
        { onSuccess: () => onOpenChange(false) }
      );
    } else {
      createNote.mutate(
        { title: title || "Untitled Note", content_md: content, tags },
        { onSuccess: () => onOpenChange(false) }
      );
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>{editingNote ? "Edit Note" : "New Note"}</DialogTitle>
        </DialogHeader>
        <div className="space-y-3 py-2">
          <div className="space-y-1.5">
            <Label>Title</Label>
            <Input value={title} onChange={(e) => setTitle(e.target.value)} placeholder="Untitled Note" />
          </div>
          <div className="space-y-1.5">
            <Label>Content (Markdown supported)</Label>
            <Textarea
              value={content}
              onChange={(e) => setContent(e.target.value)}
              rows={8}
              placeholder="Write your note..."
            />
          </div>
          <div className="space-y-1.5">
            <Label>Tags (comma-separated)</Label>
            <Input value={tagsInput} onChange={(e) => setTagsInput(e.target.value)} placeholder="ai, research" />
          </div>
        </div>
        <DialogFooter>
          <Button onClick={handleSave} disabled={isSaving}>
            {isSaving ? "Saving..." : "Save"}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}