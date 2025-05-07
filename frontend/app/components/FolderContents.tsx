"use client";
import React, { useState, useRef, useEffect } from "react";
import {
  Folder,
  File as FileIcon,
  Upload,
  X,
  ChevronLeft,
  ChevronRight,
} from "lucide-react";
import { Folder as FolderType } from "@/lib/types";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
} from "@/components/ui/dialog";
import { PDFViewer } from "@react-pdf/renderer";

interface UploadedFile {
  id: string;
  name: string;
  url: string;
}

interface FolderContentsProps {
  folder: FolderType;
  onFolderClick: (folderId: string) => void;
}

export default function FolderContents({
  folder,
  onFolderClick,
}: FolderContentsProps) {
  const [files, setFiles] = useState<UploadedFile[]>([]);
  const [isUploading, setIsUploading] = useState(false);
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [selectedFiles, setSelectedFiles] = useState<globalThis.File[]>([]);
  const [previewFile, setPreviewFile] = useState<UploadedFile | null>(null);
  const [presignedUrl, setPresignedUrl] = useState<string | null>(null);

  useEffect(() => {
    // Fetch files for the current folder when component mounts or folder changes
    const fetchFiles = async () => {
      try {
        const token = localStorage.getItem("token");
        const response = await fetch(
          `http://localhost:8000/folders/${folder.id}/files`,
          {
            headers: {
              Authorization: `Bearer ${token}`,
            },
          }
        );
        if (!response.ok) {
          throw new Error(`Failed to fetch files: ${response.status}`);
        }
        const data = await response.json();
        // Assume data is an array of files with id, url, and filename
        setFiles(
          data.map((file: any) => ({
            id: file.id,
            name: file.filename,
            url: file.url,
          }))
        );
      } catch (error) {
        console.error("Error fetching files:", error);
      }
    };
    fetchFiles();
  }, [folder.id]);

  const handleFileSelect = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      const fileList = Array.from(e.target.files);
      setSelectedFiles((prev) => [...prev, ...fileList]);
    }
  };

  const removeFile = (index: number) => {
    setSelectedFiles(selectedFiles.filter((_, i) => i !== index));
  };

  const handleUpload = async () => {
    if (selectedFiles.length === 0) {
      console.log("No files selected");
      return;
    }
    setIsUploading(true);
    try {
      const formData = new FormData();
      selectedFiles.forEach((file) => {
        formData.append("file", file);
      });
      formData.append("folder_id", folder.id);

      const token = localStorage.getItem("token");
      const response = await fetch("http://localhost:8000/upload", {
        method: "POST",
        body: formData,
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      const responseText = await response.text();

      if (!response.ok) {
        throw new Error(`Upload failed: ${response.status} ${responseText}`);
      }

      const uploadedFile = JSON.parse(responseText);
      setFiles((prevFiles) => [
        ...prevFiles,
        {
          id: uploadedFile.file_id,
          name: uploadedFile.filename,
          url: uploadedFile.url,
        },
      ]);
      setSelectedFiles([]);
      setIsDialogOpen(false);
    } catch (error) {
      console.error("Error uploading files:", error);
    } finally {
      setIsUploading(false);
    }
  };

  // Function to get presigned URL
  const getPresignedUrl = async (fileId: string) => {
    try {
      const token = localStorage.getItem("token");
      const response = await fetch(
        `http://localhost:8000/files/${fileId}/preview`,
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );
      if (!response.ok) {
        throw new Error("Failed to get preview URL");
      }
      const data = await response.json();
      return data.url;
    } catch (error) {
      console.error("Error getting preview URL:", error);
      return null;
    }
  };

  // Update preview file handler
  const handlePreviewFile = async (file: UploadedFile) => {
    setPreviewFile(file);
    setPresignedUrl(null);

    const url = await getPresignedUrl(file.id);
    if (url) {
      setPresignedUrl(url);
    }
  };

  return (
    <div className="p-4">
      <div className="mb-4">
        <h2 className="text-xl font-semibold">{folder.name}</h2>
        {folder.description && (
          <p className="text-gray-600 mt-1">{folder.description}</p>
        )}
      </div>

      <div className="mb-4">
        <Button
          variant="outline"
          onClick={() => setIsDialogOpen(true)}
          disabled={isUploading}
        >
          <Upload className="h-4 w-4 mr-2" />
          Upload PDF
        </Button>
      </div>

      <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Upload PDF Files</DialogTitle>
            <DialogDescription>Choose files to upload</DialogDescription>
          </DialogHeader>
          <div
            className="mt-4 p-8 border-dashed border-2 rounded-lg flex flex-col items-center justify-center cursor-pointer hover:bg-gray-50"
            onClick={() => fileInputRef.current?.click()}
          >
            <input
              ref={fileInputRef}
              type="file"
              multiple
              accept=".pdf"
              onChange={handleFileSelect}
              className="hidden"
            />
            <Upload className="h-12 w-12 text-gray-400 mb-4" />
            <p className="text-sm text-center text-gray-500">
              Click to select files
            </p>
          </div>

          {selectedFiles.length > 0 && (
            <div className="mt-4">
              <h4 className="text-lg font-semibold mb-2">Selected Files</h4>
              <div className="space-y-2">
                {selectedFiles.map((file, index) => (
                  <div
                    key={index}
                    className="flex items-center justify-between p-2 bg-gray-50 rounded"
                  >
                    <div className="flex items-center gap-2">
                      <FileIcon className="w-4 h-4 text-blue-500" />
                      <span className="text-sm">{file.name}</span>
                    </div>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={(e) => {
                        e.stopPropagation();
                        removeFile(index);
                      }}
                    >
                      <X className="w-4 h-4" />
                    </Button>
                  </div>
                ))}
              </div>
            </div>
          )}

          <div className="flex justify-end gap-2 mt-6">
            <Button onClick={handleUpload} disabled={isUploading}>
              {isUploading ? "Uploading..." : "Upload"}
            </Button>
            <Button
              variant="outline"
              onClick={() => setIsDialogOpen(false)}
              type="submit"
              disabled={isUploading}
            >
              Cancel
            </Button>
          </div>
        </DialogContent>
      </Dialog>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {files.map((file) => (
          <div
            key={file.id}
            className="flex items-center gap-2 p-3 bg-white rounded shadow hover:bg-gray-50 cursor-pointer"
            onClick={() => handlePreviewFile(file)}
          >
            <FileIcon className="h-5 w-5 text-gray-500" />
            <span className="truncate">{file.name}</span>
            <Button
              variant="ghost"
              size="sm"
              onClick={async (e) => {
                e.stopPropagation();
                const token = localStorage.getItem("token");
                const res = await fetch(
                  `http://localhost:8000/files/${file.id}`,
                  {
                    method: "DELETE",
                    headers: { Authorization: `Bearer ${token}` },
                  }
                );
                if (res.ok) {
                  setFiles(files.filter((f) => f.id !== file.id));
                } else {
                  alert("Failed to delete file");
                }
              }}
            >
              <X className="w-4 h-4" />
            </Button>
          </div>
        ))}
      </div>

      <Dialog
        open={!!previewFile}
        onOpenChange={(open) => {
          if (!open) {
            setPreviewFile(null);
            setPresignedUrl(null);
          }
        }}
      >
        <DialogContent className="max-w-4xl w-full h-[90vh] flex flex-col">
          <DialogHeader>
            <DialogTitle>Preview: {previewFile?.name}</DialogTitle>
          </DialogHeader>
          {previewFile && presignedUrl ? (
            <div className="flex-1 w-full flex flex-col">
              <iframe
                src={presignedUrl}
                className="flex-1 w-full h-full border-0"
                title={previewFile.name}
              />
            </div>
          ) : (
            <div className="flex items-center justify-center h-[70vh]">
              Loading PDF...
            </div>
          )}
        </DialogContent>
      </Dialog>
    </div>
  );
}
