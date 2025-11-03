// src/components/Chatbot/ChatbotUI.js
import React, { useState, useEffect } from "react";
import MessageBubble from "./MessageBubble";
import { sendMessage, getChatHistory } from "@/services/chatbot";

const ChatbotUI = () => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);

  // 🧠 Load chat history on first render
  useEffect(() => {
    async function loadHistory() {
      try {
        const history = await getChatHistory();
        if (Array.isArray(history)) setMessages(history);
      } catch (err) {
        console.error("Failed to load chat history:", err);
      }
    }
    loadHistory();
  }, []);

  // 💬 Send message handler
  const handleSend = async (e) => {
    e.preventDefault();
    if (!input.trim()) return;

    const userMessage = { sender: "user", message: input };
    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setLoading(true);

    try {
      const aiResponse = await sendMessage(input);
      const aiMessage = { sender: "ai", message: aiResponse.message };
      setMessages((prev) => [...prev, aiMessage]);
    } catch (err) {
      console.error("Chat Error:", err);
      const errorMessage = {
        sender: "ai",
        message: "⚠️ Error: Could not connect to AI backend.",
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col w-full max-w-2xl mx-auto h-[80vh] bg-white shadow-lg rounded-2xl p-4">
      {/* Chat display area */}
      <div className="flex-1 overflow-y-auto mb-4">
        {messages.map((msg, idx) => (
          <MessageBubble key={idx} sender={msg.sender} message={msg.message} />
        ))}
        {loading && <p className="text-gray-400 mt-2">AI is thinking...</p>}
      </div>

      {/* Input section */}
      <form onSubmit={handleSend} className="flex">
        <input
          type="text"
          className="flex-1 border rounded-l-lg px-3 py-2 focus:outline-none"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Type your message..."
        />
        <button
          type="submit"
          disabled={loading}
          className={`bg-blue-600 text-white px-4 rounded-r-lg hover:bg-blue-700 ${
            loading ? "opacity-60 cursor-not-allowed" : ""
          }`}
        >
          Send
        </button>
      </form>
    </div>
  );
};

export default ChatbotUI;
// frontend/src/components/Chatbot/ChatbotUI.js
import { useEffect, useState } from "react";
import { sendMessage, getChatHistory } from "@/services/chatbot";
import MessageBubble from "./MessageBubble";

export default function ChatbotUI() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [summary, setSummary] = useState("");

  useEffect(() => {
    getChatHistory().then((data) => {
      setMessages(data);
      const systemSummary = data.find(m => m.role === "system" && m.content.startsWith("Conversation summary"));
      if (systemSummary) setSummary(systemSummary.content);
    });
  }, []);

  const handleSend = async () => {
    if (!input.trim()) return;
    const userMsg = { role: "user", content: input };
    setMessages((prev) => [...prev, userMsg]);
    setInput("");

    const res = await sendMessage(input);
    setMessages((prev) => [...prev, { role: "assistant", content: res.reply }]);
  };

  return (
    <div className="flex flex-col h-screen p-4 bg-gray-50">
      {summary && (
        <div className="p-3 bg-yellow-100 rounded-lg mb-3 text-sm text-gray-700">
          🧠 <b>Conversation Summary:</b> {summary.replace("Conversation summary:", "")}
        </div>
      )}
      <div className="flex-1 overflow-y-auto space-y-2">
        {messages.map((msg, i) => (
          <MessageBubble key={i} role={msg.role} content={msg.content} />
        ))}
      </div>
      <div className="flex mt-4">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          className="flex-1 border rounded-l-lg p-2"
          placeholder="Type your message..."
        />
        <button onClick={handleSend} className="bg-blue-600 text-white px-4 py-2 rounded-r-lg">
          Send
        </button>
      </div>
    </div>
  );
}
