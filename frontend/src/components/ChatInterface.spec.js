import React from "react";
import { render, screen, fireEvent } from "@testing-library/react";
import "@testing-library/jest-dom"; // For extra matchers like .toBeDisabled()

import ChatInterface from "./ChatInterface";
import { useChatbotMessages } from "../hooks/useChatbotMessages";

// Mock the custom hook
jest.mock("../hooks/useChatbotMessages");

// Helper to set up mock hook values
const setupMockHook = (mockValues = {}) => {
  useChatbotMessages.mockReturnValue({
    messages: [],
    isLoading: false,
    error: null,
    sendMessage: jest.fn(), // Default mock function
    ...mockValues, // Override defaults with provided values
  });
};

describe("ChatInterface Component", () => {
  beforeEach(() => {
    useChatbotMessages.mockClear();
    setupMockHook();
  });

  it("renders initial UI correctly", () => {
    render(<ChatInterface />);

    expect(
      screen.getByPlaceholderText(/enter your measurements/i)
    ).toBeInTheDocument();
    expect(
      screen.getByRole("button", { name: /get recommendation/i })
    ).toBeInTheDocument();
    expect(
      screen.getByRole("button", { name: /get recommendation/i })
    ).toBeDisabled();
  });

  it("calls sendMessage on form submission", () => {
    const mockSendMessage = jest.fn();
    setupMockHook({ sendMessage: mockSendMessage });

    render(<ChatInterface />);

    const input = screen.getByPlaceholderText(/enter your measurements/i);
    const button = screen.getByRole("button", { name: /get recommendation/i });
    expect(button).toBeDisabled();
    const testMessage = "34 underbust, 38 bust";
    fireEvent.change(input, { target: { value: testMessage } });
    fireEvent.click(button);

    expect(mockSendMessage).toHaveBeenCalledTimes(1);
    expect(mockSendMessage).toHaveBeenCalledWith(testMessage);
  });

  it("displays messages from the hook", () => {
    const mockMessages = [
      { text: "User message", isUser: true },
      {
        text: "Bot response",
        isUser: false,
        reasoning: "Reason",
        fitTips: "Tips",
      },
    ];
    setupMockHook({ messages: mockMessages });

    render(<ChatInterface />);

    expect(screen.getByText("User message")).toBeInTheDocument();
    expect(screen.getByText("Bot response")).toBeInTheDocument();
    expect(screen.getByText("Reason")).toBeInTheDocument();
    expect(screen.getByText("Tips")).toBeInTheDocument();
  });

  it("shows loading state when isLoading is true", () => {
    setupMockHook({ isLoading: true });

    render(<ChatInterface />);

    expect(screen.getByRole("button", { name: /Loading.../i })).toBeDisabled();
    expect(screen.getByTestId("loading-spinner")).toBeInTheDocument();
  });

  it("displays error message when error exists", () => {
    const mockError = new Error("Something went wrong");
    setupMockHook({ error: mockError });

    render(<ChatInterface />);

    expect(screen.getByText(mockError.message)).toBeInTheDocument();
  });
});
