import React, { useState } from "react";
import "../styles/Chat.css";
import { useChatbotMessages } from "../hooks/useChatbotMessages";
import Message from "./Message";

const ChatInterface = () => {
  const {
    sendMessage,
    isLoading,
    messages: chatbotMessages,
    error,
  } = useChatbotMessages();
  const [input, setInput] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    sendMessage(input);
    setInput("");
  };

  return (
    <div className="chat-container">
      <div className="messages">
        {chatbotMessages.map((msg, index) => (
          <Message key={index} message={msg} isUser={msg.isUser} />
        ))}
        {isLoading && <div className="spinner"></div>}
      </div>
      <form onSubmit={handleSubmit} className="input-form">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Enter your measurements and fit issues..."
        />
        <button type="submit" disabled={isLoading || !input}>
          {isLoading ? "Loading..." : "Get Recommendation"}
        </button>
      </form>
      {error && <div className="error">{error.message}</div>}
    </div>
  );
};

export default ChatInterface;
