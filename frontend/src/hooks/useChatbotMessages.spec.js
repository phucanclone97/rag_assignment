import { renderHook, act } from "@testing-library/react";
import { useChatbotMessages } from "./useChatbotMessages";

// Mock global fetch
global.fetch = jest.fn();

describe("useChatbotMessages Hook", () => {
  beforeEach(() => {
    // Reset fetch mock before each test
    fetch.mockClear();
  });

  it("should initialize with correct default state", () => {
    const { result } = renderHook(() => useChatbotMessages());

    expect(result.current.messages).toEqual([]);
    expect(result.current.isLoading).toBe(false);
    expect(result.current.error).toBeNull();
  });

  it("should handle successful message sending", async () => {
    const mockResponse = {
      recommendation: "34D",
      reasoning: "Test reasoning",
      fit_tips: "Test tips",
      identified_issues: ["test_issue"],
      confidence: 0.9,
    };
    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => mockResponse,
    });

    const { result, waitForNextUpdate } = renderHook(() =>
      useChatbotMessages()
    );

    // Use act to wrap state updates triggered by async operations
    await act(async () => {
      result.current.sendMessage("Test input");
    });

    // Wait for async operations and state updates to complete
    // Note: waitForNextUpdate might not be needed depending on RTL version/setup
    // await waitForNextUpdate(); // Or use waitFor from @testing-library/react

    expect(result.current.isLoading).toBe(false);
    expect(result.current.error).toBeNull();
    expect(result.current.messages).toHaveLength(2);
    expect(result.current.messages[0]).toEqual({
      text: "Test input",
      isUser: true,
    });
    expect(result.current.messages[1]).toEqual({
      text: `Recommended Size: ${mockResponse.recommendation}`,
      reasoning: mockResponse.reasoning,
      fitTips: mockResponse.fit_tips,
      issues: mockResponse.identified_issues, // Corrected key from hook
      confidence: mockResponse.confidence,
      isUser: false,
    });
  });

  it("should handle API error response", async () => {
    const mockError = { detail: "Invalid request" };
    fetch.mockResolvedValueOnce({
      ok: false,
      status: 400,
      json: async () => mockError,
    });

    const { result, waitForNextUpdate } = renderHook(() =>
      useChatbotMessages()
    );

    await act(async () => {
      result.current.sendMessage("Bad input");
    });

    // await waitForNextUpdate(); // Or waitFor

    expect(result.current.isLoading).toBe(false);
    expect(result.current.messages).toEqual([]); // Messages should not update on error
    expect(result.current.error).toBeInstanceOf(Error);
    expect(result.current.error.message).toBe(mockError.detail); // Check error message extraction
  });

  it("should handle network error", async () => {
    const networkError = new Error("Network failed");
    fetch.mockRejectedValueOnce(networkError);

    const { result, waitForNextUpdate } = renderHook(() =>
      useChatbotMessages()
    );

    await act(async () => {
      result.current.sendMessage("Input causing network error");
    });

    // await waitForNextUpdate(); // Or waitFor

    expect(result.current.isLoading).toBe(false);
    expect(result.current.messages).toEqual([]);
    expect(result.current.error).toBe(networkError); // Should capture the exact error
  });

  it("should clear error on subsequent successful call", async () => {
    // First, trigger an error
    const mockError = { detail: "Initial error" };
    fetch.mockResolvedValueOnce({
      ok: false,
      status: 400,
      json: async () => mockError,
    });

    const { result, waitForNextUpdate } = renderHook(() =>
      useChatbotMessages()
    );

    await act(async () => {
      result.current.sendMessage("Trigger error");
    });
    // await waitForNextUpdate();
    expect(result.current.error).not.toBeNull(); // Error should be set

    // Now, trigger a successful call
    const mockSuccessResponse = { recommendation: "32B" };
    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => mockSuccessResponse,
    });

    await act(async () => {
      result.current.sendMessage("Successful input");
    });
    // await waitForNextUpdate();

    expect(result.current.isLoading).toBe(false);
    expect(result.current.error).toBeNull(); // Error should be cleared
    expect(result.current.messages).toHaveLength(2); // Messages should update
  });
});
