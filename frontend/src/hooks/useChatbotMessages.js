import { useState } from "react";

export const useChatbotMessages = () => {
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  const sendMessage = async (inputMessage) => {
    try {
      setIsLoading(true);
      const response = await fetch("http://localhost:8000/api/bra-fitting", {
        method: "POST",
        body: JSON.stringify({ text: inputMessage }),
      });

      // if (!response.ok) {
      //   throw new Error(response.body);
      // }

      const data = await response.json();
      console.log(data);
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
      console.log("Error in useChatbotMessages");
      console.log({ error });
      console.error("Error sending message:", error);
      setError(error);
      setIsLoading(false);
    } finally {
      setIsLoading(false);
    }
  };

  return { messages, isLoading, sendMessage, error };
};
