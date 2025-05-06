"use client";
import React, { useState, useEffect } from "react";
import Sidebar from "../components/Sidebar";
import Folders from "../components/FolderGrid";
import { Folder } from "@/lib/types";

export default function Dashboard() {
  const [folders, setFolders] = useState<Folder[]>([]);
  const [error, setError] = useState<string | null>(null);

  const fetchFolders = async () => {
    try {
      setError(null);
      const token = localStorage.getItem("token");
      if (!token) {
        throw new Error("No authentication token found. Please sign in again.");
      }

      const response = await fetch("http://localhost:8000/folders", {
        headers: { Authorization: `Bearer ${token}` },
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => null);
        throw new Error(
          errorData?.detail ||
            `Failed to fetch folders (Status: ${response.status})`
        );
      }

      const data = await response.json();
      if (!data || !data.folders || !Array.isArray(data.folders)) {
        throw new Error("Server returned unexpected data format");
      }

      setFolders(data.folders);
    } catch (error) {
      if (error instanceof Error) {
        setError(error.message);
      } else {
        setError("Failed to fetch folders");
      }
    }
  };

  useEffect(() => {
    fetchFolders();
  }, []);

  const handleCreateFolder = async (
    name: string,
    description: string | null
  ) => {
    try {
      setError(null);
      const token = localStorage.getItem("token");
      if (!token) {
        throw new Error("No authentication token found. Please sign in again.");
      }

      const response = await fetch("http://localhost:8000/folders", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ name, description }),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => null);
        throw new Error(
          errorData?.detail ||
            `Failed to create folder (Status: ${response.status})`
        );
      }

      await fetchFolders();
    } catch (error) {
      if (error instanceof Error) {
        setError(error.message);
      } else {
        setError("Failed to create folder");
      }
    }
  };

  const handleRenameFolder = async (
    id: string,
    name: string,
    description: string | null
  ) => {
    try {
      setError(null);
      const token = localStorage.getItem("token");
      if (!token) {
        throw new Error("No authentication token found. Please sign in again.");
      }

      const response = await fetch(`http://localhost:8000/folders/${id}`, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ name, description }),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => null);
        throw new Error(
          errorData?.detail ||
            `Failed to update folder (Status: ${response.status})`
        );
      }

      await fetchFolders();
    } catch (error) {
      if (error instanceof Error) {
        setError(error.message);
      } else {
        setError("Failed to update folder");
      }
      throw error;
    }
  };

  const handleDeleteFolder = async (id: string) => {
    try {
      setError(null);
      const token = localStorage.getItem("token");
      if (!token) {
        throw new Error("No authentication token found");
      }

      const response = await fetch(`http://localhost:8000/folders/${id}`, {
        method: "DELETE",
        headers: { Authorization: `Bearer ${token}` },
      });

      if (!response.ok) {
        throw new Error("Failed to delete folder");
      }

      await fetchFolders();
    } catch (error) {
      if (error instanceof Error) {
        setError(error.message);
      } else {
        setError("Failed to delete folder");
      }
    }
  };

  return (
    <div className="flex h-screen bg-gray-100">
      <div className="w-64 border-r bg-white">
        <Sidebar onCreateFolder={handleCreateFolder} />
      </div>
      <div className="flex-1 overflow-auto p-6">
        {error && (
          <div className="mb-4 p-4 bg-red-100 text-red-700 rounded">
            {error}
          </div>
        )}
        <Folders
          folders={folders}
          onRename={handleRenameFolder}
          onDelete={handleDeleteFolder}
        />
      </div>
    </div>
  );
}
