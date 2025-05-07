import React, { useState, useEffect, useRef } from "react";
import { Button } from "@/components/ui/button";
import { MessageCircle, X } from "lucide-react";

interface ChatMessage {
  role: "user" | "assistant";
  content: string;
}

export default function ChatWindow() {
  const [isChatOpen, setIsChatOpen] = useState(false);
  const [chatMessages, setChatMessages] = useState<ChatMessage[]>([
    {
      role: "assistant",
      content: "Hello! How can I help you today?",
    },
  ]);
  const [inputMessage, setInputMessage] = useState("");
  const endOfMessagesRef = useRef<HTMLDivElement>(null);

  useEffect (() => {
    endOfMessagesRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [chatMessages]);

  const handleSendMessage = async () => {
    if (inputMessage.trim() === "") return;

    const userMessage: ChatMessage = {
      role: "user",
      content: inputMessage,
    };

    setChatMessages((prevMessages) => [...prevMessages, userMessage]);
    setInputMessage(""); // clear the input field

    try {
      const token = localStorage.getItem("token");
      const response = await fetch("http://localhost:8000/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          message: inputMessage,
        }),
      });

      if (!response.ok) {
        throw new Error("Failed to get a response");
      }

      const data = await response.json();
      const assistantMessage: ChatMessage = {
        role: "assistant",
        content: data.response,
      };

      setChatMessages((prevMessages) => [...prevMessages, assistantMessage]);
    } catch (error) {
      console.error("Error sending message:", error);
      const errorMessage: ChatMessage = {
        role: "assistant",
        content:
          "An error occurred while sending the message. Please try again.",
      };
      setChatMessages((prevMessages) => [...prevMessages, errorMessage]);
    }
  };

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

          <div className="flex-1 overflow-y-auto p-4 space-y-4">
            {chatMessages.map((message, index) => (
              <div
                key={index}
                className={`flex ${
                  message.role === "user" ? "justify-end" : "justify-start"
                }`}
              >
                <div
                  className={`max-w-[80%] p-3 rounded-lg ${
                    message.role === "user"
                      ? "bg-black text-white"
                      : "bg-gray-100 text-gray-900"
                  }`}
                >
                  {message.content}
                </div>
              </div>
            ))}
            <div ref={endOfMessagesRef} />
          </div>

          <div className="p-4 border-t">
            <div className="flex gap-2">
              <input
                type="text"
                value={inputMessage}
                onChange={(e) => setInputMessage(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === "Enter" && !e.shiftKey) {
                    e.preventDefault();
                    handleSendMessage();
                  }
                }}
                placeholder="Type your message..."
                className="flex-1 px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-black"
              />
              <Button onClick={handleSendMessage}>Send</Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
