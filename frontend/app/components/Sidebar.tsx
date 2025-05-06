"use client";
import React, { useState } from "react";
import { Plus, FolderPlus } from "lucide-react";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
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

interface SidebarProps {
  onCreateFolder: (name: string, description: string | null) => void;
}

export default function Sidebar({ onCreateFolder }: SidebarProps) {
  const [isNewFolderDialogOpen, setIsNewFolderDialogOpen] = useState(false);
  const [folderName, setFolderName] = useState("");
  const [folderDescription, setFolderDescription] = useState("");

  const handleNewFolder = () => {
    setIsNewFolderDialogOpen(true);
  };

  const handleCreateFolder = (e: React.FormEvent) => {
    e.preventDefault();
    const name = folderName.trim() || "Untitled Folder";
    const description = folderDescription.trim() || null;
    onCreateFolder(name, description);
    setFolderName("");
    setFolderDescription("");
    setIsNewFolderDialogOpen(false);
  };

  return (
    <div className="w-64 bg-white border-r h-full flex flex-col p-2">
      <DropdownMenu>
        <DropdownMenuTrigger asChild>
          <Button variant="outline" className="flex items-center gap-2 w-full">
            <Plus className="h-4 w-4" /> New
          </Button>
        </DropdownMenuTrigger>
        <DropdownMenuContent>
          <DropdownMenuItem onClick={handleNewFolder}>
            <FolderPlus className="h-4 w-4" />
            New Folder
          </DropdownMenuItem>
        </DropdownMenuContent>
      </DropdownMenu>

      <Dialog
        open={isNewFolderDialogOpen}
        onOpenChange={setIsNewFolderDialogOpen}
      >
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Create New Folder</DialogTitle>
            <DialogDescription>
              Create a new folder to organize your files.
            </DialogDescription>
          </DialogHeader>
          <form onSubmit={handleCreateFolder}>
            <div className="grid gap-4 py-4">
              <div className="grid gap-2">
                <Label htmlFor="folderName">Folder Name</Label>
                <Input
                  id="folderName"
                  value={folderName}
                  onChange={(e) => setFolderName(e.target.value)}
                  placeholder="Enter folder name"
                  autoFocus
                />
              </div>
              <div className="grid gap-2">
                <Label htmlFor="folderDescription">
                  Description (optional)
                </Label>
                <Textarea
                  id="folderDescription"
                  value={folderDescription}
                  onChange={(e: React.ChangeEvent<HTMLTextAreaElement>) =>
                    setFolderDescription(e.target.value)
                  }
                  placeholder="Enter folder description"
                  rows={3}
                />
              </div>
            </div>
            <DialogFooter>
              <Button
                type="button"
                variant="outline"
                onClick={() => setIsNewFolderDialogOpen(false)}
              >
                Cancel
              </Button>
              <Button type="submit">Create</Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>
    </div>
  );
}
