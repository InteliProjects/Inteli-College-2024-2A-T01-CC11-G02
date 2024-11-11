"use client";
import { useEffect, useState } from "react";
import ChatInput from "./input";
import ChatLabel from "./label";

export default function ChatBox() {
  const [messages, setMessages] = useState<any[]>([]);

  useEffect(() => {
    console.log(messages);
  }, [messages]);

  return (
    <div className="test flex rounded-md p-4 bg-slate-700 w-80 justify-end items-center flex-col gap-2 ml-auto">
      <ChatLabel messages={messages} setMessage={setMessages} />
      <ChatInput messages={messages} setMessage={setMessages} />
    </div>
  );
}
