import { useState } from "react";

export const useChatbotMessages = () => {
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  const sendMessage = async (inputMessage) => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await fetch("http://localhost:8000/api/bra-fitting", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ text: inputMessage }),
      });

      if (!response.ok) {
        let errorPayload = null;
        try {
          errorPayload = await response.json();
        } catch (parseError) {
          console.error("Failed to parse error response body:", parseError);
        }
        const errorMessage =
          errorPayload?.detail?.[0]?.msg ||
          errorPayload?.message ||
          (errorPayload ? JSON.stringify(errorPayload) : null) ||
          `Request failed with status ${response.status}${
            response.statusText ? ": " + response.statusText : ""
          }`;

        throw new Error(errorMessage);
      }

      const data = await response.json();
      setMessages([
        ...messages,
        {
          text: inputMessage,
          isUser: true,
        },
        {
          text: `Recommended Size: ${data.recommendation}`,
          reasoning: data.reasoning,
          fitTips: data.fit_tips,
          issues: data.identified_issues,
          confidence: data.confidence,
          isUser: false,
        },
      ]);
      setIsLoading(false);
    } catch (error) {
      console.error("Error sending message:", error);
      setError(error);
      setIsLoading(false);
    } finally {
      setIsLoading(false);
    }
  };

  return { messages, isLoading, sendMessage, error };
};
