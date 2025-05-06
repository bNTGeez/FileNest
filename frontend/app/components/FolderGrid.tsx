import React from "react";
import { Folder } from "lucide-react";

interface Folder {
  id: string;
  name: string;
}

interface FolderGridProps {
  folders: Folder[];
}

export default function FolderGrid({ folders }: FolderGridProps) {
  return (
    <div className="grid grid-cols-3 gap-4 p-6">
      {folders.map((folder) => (
        <div
          key={folder.id}
          className="flex items-center gap-2 bg-white rounded shadow p-4 hover:bg-gray-100 cursor-pointer"
        >
          <Folder className="h-6 w-6 text-blue-500" />
          <span className="truncate font-medium">{folder.name}</span>
        </div>
      ))}
    </div>
  );
}
