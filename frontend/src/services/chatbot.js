// frontend/src/services/chatbot.js

import api from "./api";

/**
 * 🧠 Send a user message to the backend chatbot
 * @param {string} message - The user's message
 * @returns {Promise<{ sender: string, message: string }>} - AI response
 */
export const sendMessage = async (message) => {
  try {
    const response = await api.post("/chat", { message });
    return {
      sender: "ai",
      message: response.data.response || "No response from AI.",
    };
  } catch (error) {
    console.error("Error sending message:", error);
    return {
      sender: "ai",
      message: "⚠️ Error: Could not connect to AI backend.",
    };
  }
};

/**
 * 💬 Fetch previous chat history from backend
 * @returns {Promise<Array<{ sender: string, message: string }>>}
 */
export const getChatHistory = async () => {
  try {
    const response = await api.get("/chat/history");
    return response.data.history || [];
  } catch (error) {
    console.error("Error fetching chat history:", error);
    return [];
  }
};
