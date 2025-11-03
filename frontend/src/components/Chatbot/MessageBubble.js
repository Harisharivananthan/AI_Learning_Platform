// src/components/Chatbot/MessageBubble.js
import React from "react";

const MessageBubble = ({ message, sender }) => {
  const isUser = sender === "user";

  return (
    <div
      className={`flex ${isUser ? "justify-end" : "justify-start"} mb-3`}
    >
      <div
        className={`max-w-xs px-4 py-2 rounded-2xl ${
          isUser
            ? "bg-blue-600 text-white rounded-br-none"
            : "bg-gray-200 text-gray-900 rounded-bl-none"
        }`}
      >
        {message}
      </div>
    </div>
  );
};

export default MessageBubble;
