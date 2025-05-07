"use client";
import React, { useEffect, useState, use } from "react";
import { Button } from "@/components/ui/button";
import FolderContents from "@/app/components/FolderContents";
import { Folder as FolderType } from "@/lib/types";
import { useRouter } from "next/navigation";

export default function FolderPage({
  params,
}: {
  params: Promise<{ folderId: string }>;
}) {
  const [folder, setFolder] = useState<FolderType | null>(null);
  const router = useRouter();
  const { folderId } = use(params);

  useEffect(() => {
    const fetchFolders = async () => {
      try {
        const token = localStorage.getItem("token");
        const response = await fetch(
          `http://localhost:8000/folders/${folderId}`,
          {
            headers: {
              Authorization: `Bearer ${token}`,
            },
          }
        );
        if (!response.ok) {
          throw new Error(`Failed to fetch folder: ${response.status}`);
        }
        const data = await response.json();
        setFolder(data);
      } catch (error) {
        console.error("Error fetching folder:", error);
        router.push("/dashboard");
      }
    };
    fetchFolders();
  }, [folderId]);

  if (!folder) {
    return <div>Loading...</div>;
  }

  return (
    <div>
      <div className="mb-4 mx-4">
        <Button
          variant="outline"
          onClick={() => router.push("/dashboard")}
          className="mb-4"
        >
          ← Back to Folders
        </Button>
      </div>
      <FolderContents folder={folder} />
    </div>
  );
}
