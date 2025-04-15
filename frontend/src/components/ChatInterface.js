import React, { useState } from "react";
import "../styles/Chat.css";

const ChatInterface = () => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  // Bug: Missing loading state
  
  const handleSubmit = async (e) => {
    e.preventDefault();
    
    try {
      // Bug: No loading indicator
      const response = await fetch("http://localhost:8000/api/bra-fitting", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ text: input })
      });

      const data = await response.json();
      
      // Bug: No error handling for failed requests
      setMessages([...messages, {
        text: input,
        isUser: true
      }, {
        text: `Recommended Size: ${data.recommendation}`,
        reasoning: data.reasoning,
        fitTips: data.fit_tips,
        issues: data.identified_issues,
        confidence: data.confidence,
        isUser: false
      }]);
      
      setInput("");
    } catch (error) {
      // Bug: Poor error handling
      console.error(error);
    }
  };

  return (
    <div className="chat-container">
      <div className="messages">
        {messages.map((msg, index) => (
          <div key={index} className={`message ${msg.isUser ? "user" : "bot"}`}>
            {msg.isUser ? (
              msg.text
            ) : (
              // Bug: Poor information display
              <div>
                <div>{msg.text}</div>
                <div>{msg.reasoning}</div>
                <div>{msg.fitTips}</div>
              </div>
            )}
          </div>
        ))}
      </div>
      <form onSubmit={handleSubmit} className="input-form">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Enter your measurements and fit issues..."
        />
        <button type="submit">Get Recommendation</button>
      </form>
    </div>
  );
};

export default ChatInterface;
