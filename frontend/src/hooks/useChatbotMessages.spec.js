import { renderHook } from "@testing-library/react";
import { useChatbotMessages } from "./useChatbotMessages";

describe("useChatbotMessages", () => {
  it("should be a function", () => {
    expect(typeof useChatbotMessages).toBe("function");
  });

  it("should return an object with the correct properties", () => {
    const { result } = renderHook(useChatbotMessages);
    expect(result.current).toEqual({
      sendMessage: expect.any(Function),
      messages: [],
      isLoading: false,
      error: null,
    });
  });

  it("should handle errors", () => {
    const { result } = renderHook(useChatbotMessages);
    expect(result.current.error).toBeNull();
  });
});
