"use client";
import React, { useState } from "react";
import { useRouter } from "next/navigation";
import { Folder, Edit2, Trash2 } from "lucide-react";
import { Folder as FolderType } from "@/lib/types";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
  DialogDescription,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";

interface FolderGridProps {
  folders: FolderType[];
  onRename: (
    id: string,
    name: string,
    description: string | null
  ) => Promise<void>;
  onDelete: (id: string) => void;
}

export default function FolderGrid({
  folders,
  onRename,
  onDelete,
}: FolderGridProps) {
  const [editingId, setEditingId] = useState<string | null>(null);
  const [editName, setEditName] = useState("");
  const [editDescription, setEditDescription] = useState<string>("");
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [folderToDelete, setFolderToDelete] = useState<string | null>(null);

  const router = useRouter();

  if (folders.length === 0) {
    return (
      <div className="grid grid-cols-3 gap-4 p-6">
        <div className="col-span-3 text-center text-gray-500">
          No folders found. Create one to get started!
        </div>
      </div>
    );
  }

  const handleSubmit = async (folderId: string) => {
    try {
      await onRename(
        folderId,
        editName.trim() || "Untitled Folder",
        editDescription.trim() || null
      );
      setEditingId(null);
    } catch (error) {
      console.error("Failed to update folder:", error);
    }
  };

  return (
    <div className="grid grid-cols-3 gap-4 p-6">
      {folders.map((folder) => (
        <div
          key={folder.id}
          className="flex flex-col gap-2 bg-white rounded shadow p-4 hover:bg-gray-100 cursor-pointer relative"
          onClick={() => router.push(`/folders/${folder.id}`)}
        >
          <div className="flex items-center gap-2">
            <Folder className="h-6 w-6 text-blue-500 shrink-0" />
            <span className="truncate font-medium flex-1">{folder.name}</span>
            <div className="flex gap-2">
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  setEditingId(folder.id);
                  setEditName(folder.name);
                  setEditDescription(folder.description || "");
                }}
                className="p-1 hover:bg-gray-200 rounded"
                title="Edit"
              >
                <Edit2 className="h-4 w-4" />
              </button>
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  setFolderToDelete(folder.id);
                  setDeleteDialogOpen(true);
                }}
                className="p-1 hover:bg-red-100 rounded"
                title="Delete"
              >
                <Trash2 className="h-4 w-4 text-red-500" />
              </button>
            </div>
          </div>
          {folder.description && (
            <p className="text-sm text-gray-600 line-clamp-2">
              {folder.description}
            </p>
          )}
        </div>
      ))}

      <Dialog
        open={editingId !== null}
        onOpenChange={(open) => !open && setEditingId(null)}
      >
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Edit Folder</DialogTitle>
            <DialogDescription>
              Edit your folder's name and description.
            </DialogDescription>
          </DialogHeader>
          <form
            onSubmit={(e) => {
              e.preventDefault();
              if (editingId) handleSubmit(editingId);
            }}
          >
            <div className="grid gap-4 py-4">
              <div className="grid gap-2">
                <Label htmlFor="editName">Name</Label>
                <Input
                  id="editName"
                  value={editName}
                  onChange={(e) => setEditName(e.target.value)}
                  placeholder="Enter folder name"
                  autoFocus
                />
              </div>
              <div className="grid gap-2">
                <Label htmlFor="editDescription">Description (optional)</Label>
                <Textarea
                  id="editDescription"
                  value={editDescription}
                  onChange={(e) => setEditDescription(e.target.value)}
                  placeholder="Enter folder description"
                  rows={3}
                />
              </div>
            </div>
            <DialogFooter>
              <Button
                type="button"
                variant="outline"
                onClick={() => setEditingId(null)}
              >
                Cancel
              </Button>
              <Button type="submit">Save Changes</Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>

      <Dialog open={deleteDialogOpen} onOpenChange={setDeleteDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Delete Folder</DialogTitle>
            <DialogDescription>
              Are you sure you want to delete this folder?
            </DialogDescription>
          </DialogHeader>
          <div>
            <Button
              variant="destructive"
              onClick={() => {
                if (folderToDelete) {
                  onDelete(folderToDelete);
                }
                setDeleteDialogOpen(false);
                setFolderToDelete(null);
              }}
            >
              Delete
            </Button>
            <Button
              variant="outline"
              onClick={() => setDeleteDialogOpen(false)}
            >
              Cancel
            </Button>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
}
