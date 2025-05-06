"use client";
import React, { useState } from "react";
import Sidebar from "../components/Sidebar";
import Folders from "../components/FolderGrid";
export default function Dashboard() {
  interface Folder {
    id: string;
    name: string;
  }

  const [folders, setFolders] = useState<Folder[]>([]);

  const handleCreateFolder = (name: string) => {
    setFolders([...folders, { id: Date.now().toString(), name }]);
  };

  return (
    <div>
      <div>
        <Sidebar onCreateFolder={handleCreateFolder} />
      </div>
      <div>
        <Folders folders={folders} />
      </div>
    </div>
  );
}
