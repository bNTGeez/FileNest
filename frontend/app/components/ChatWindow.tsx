import React, { useState } from "react";
import { Button } from "@/components/ui/button";
import { MessageCircle, X } from "lucide-react";

export default function ChatWindow() {
  const [isChatOpen, setIsChatOpen] = useState(false);

  return (
    <div>
      <div className="fixed right-4 bottom-4">
        <Button
          variant="outline"
          size="icon"
          className={
            isChatOpen
              ? "hidden"
              : "rounded-full h-12 w-12 bg-black hover:bg-black/80"
          }
          onClick={() => setIsChatOpen(!isChatOpen)}
        >
          <MessageCircle className="w-6 h-6 text-white" />
        </Button>
      </div>

      {isChatOpen && (
        <div className="fixed right-4 bottom-4 w-96 h-[500px] bg-white rounded-lg shadow-lg border flex flex-col z-40">
          <div className="p-4 border-b flex justify-between items-center">
            <h3 className="font-semibold">Chat</h3>
            <Button
              variant="ghost"
              size="icon"
              className="h-8 w-8"
              onClick={() => setIsChatOpen(false)}
            >
              <X className="h-4 w-4" />
            </Button>
          </div>

          <div className="flex-1 overflow-y-auto p-4">
            {/* will have the chat messages go here */}
          </div>

          <div className="p-4 border-t">
            <div className="flex gap-2">
              <input
                type="text"
                placeholder="Type your message..."
                className="flex-1 px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-black"
              />
              <Button>Send</Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
