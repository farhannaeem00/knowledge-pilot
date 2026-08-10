"use client";

import { useEffect, useRef, useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import { MessageSquare, Bot, Loader2 } from "lucide-react";
import { useChatMessages, useSendMessage } from "@/hooks/use-chat";
import { ThreadList } from "@/components/chat/thread-list";
import { MessageBubble } from "@/components/chat/message-bubble";
import { ChatInput } from "@/components/chat/chat-input";
import { Skeleton } from "@/components/ui/skeleton";

export default function ChatPage() {
  const params = useParams<{ workspaceId: string; documentId: string }>();
  const { workspaceId, documentId } = params;
  const [activeThreadId, setActiveThreadId] = useState<string | null>(null);
  const scrollRef = useRef<HTMLDivElement>(null);

  const { data: messages, isLoading: messagesLoading } = useChatMessages(workspaceId, documentId, activeThreadId);
  const sendMessage = useSendMessage(workspaceId, documentId, activeThreadId);

  useEffect(() => {
    scrollRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, sendMessage.isPending]);

  const handleSend = (content: string) => {
    if (!activeThreadId) return;
    sendMessage.mutate(content);
  };

  return (
    <div className="mx-auto flex h-[calc(100vh-8rem)] max-w-5xl flex-col">
      <div className="mb-4">
        <p className="text-sm text-muted-foreground">
          <Link href={`/workspaces/${workspaceId}/documents/${documentId}`} className="hover:underline">
            ← Back to document
          </Link>
        </p>
        <h1 className="flex items-center gap-2 text-xl font-bold">
          <MessageSquare className="h-5 w-5 text-primary" />
          Chat
        </h1>
      </div>

      <div className="flex flex-1 overflow-hidden rounded-lg border border-border">
        <ThreadList
          workspaceId={workspaceId}
          documentId={documentId}
          activeThreadId={activeThreadId}
          onSelectThread={setActiveThreadId}
        />

        <div className="flex flex-1 flex-col">
          {!activeThreadId ? (
            <div className="flex flex-1 flex-col items-center justify-center gap-2 text-center">
              <Bot className="h-10 w-10 text-muted-foreground" />
              <p className="text-muted-foreground">Select or create a thread to start chatting.</p>
            </div>
          ) : (
            <>
              <div className="flex-1 space-y-4 overflow-y-auto p-4">
                {messagesLoading ? (
                  <>
                    <Skeleton className="h-12 w-2/3" />
                    <Skeleton className="ml-auto h-12 w-1/2" />
                  </>
                ) : messages && messages.length > 0 ? (
                  <>
                    {messages.map((msg) => (
                      <MessageBubble key={msg.id} message={msg} />
                    ))}
                    {sendMessage.isPending && (
                      <div className="flex items-center gap-2 text-sm text-muted-foreground">
                        <Loader2 className="h-3.5 w-3.5 animate-spin" />
                        Thinking...
                      </div>
                    )}
                    <div ref={scrollRef} />
                  </>
                ) : (
                  <p className="text-center text-sm text-muted-foreground">
                    Ask anything about this document.
                  </p>
                )}
              </div>
              <ChatInput onSend={handleSend} disabled={sendMessage.isPending} />
            </>
          )}
        </div>
      </div>
    </div>
  );
}