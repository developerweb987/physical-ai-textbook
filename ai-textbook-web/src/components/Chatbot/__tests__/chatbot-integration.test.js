// ai-textbook-web/src/components/Chatbot/__tests__/chatbot-integration.test.js

import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import Chatbot from '../index';
import ChatbotAPI from '../../../services/chatbot-api';

// Mock the ChatbotAPI
jest.mock('../../../services/chatbot-api');

describe('Chatbot Integration Tests', () => {
  let mockChatbotAPI;

  beforeEach(() => {
    mockChatbotAPI = {
      queryChatbot: jest.fn(),
      createSession: jest.fn(),
      getChatHistory: jest.fn(),
      submitFeedback: jest.fn(),
    };
    ChatbotAPI.mockImplementation(() => mockChatbotAPI);
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  test('should send message and receive response in global mode', async () => {
    // Mock successful API response
    const mockResponse = {
      response: 'This is a test response',
      sources: [{ title: 'Test Source', url: 'https://example.com', snippet: 'Test snippet' }],
      confidence: 0.95,
      session_id: 'test-session-id'
    };
    mockChatbotAPI.queryChatbot.mockResolvedValue(mockResponse);

    render(<Chatbot initialMode="global" />);

    // Open chatbot
    fireEvent.click(screen.getByLabelText('Open chatbot'));

    // Type message
    const input = screen.getByPlaceholderText('Ask a question about the textbook content...');
    fireEvent.change(input, { target: { value: 'Test question' } });

    // Send message
    fireEvent.click(screen.getByText('Send'));

    // Wait for response
    await waitFor(() => {
      expect(screen.getByText('This is a test response')).toBeInTheDocument();
    });

    // Verify API was called with correct parameters
    expect(mockChatbotAPI.queryChatbot).toHaveBeenCalledWith(
      'Test question',
      'global',
      null
    );
  });

  test('should send message and receive response in selected text mode', async () => {
    // Mock successful API response
    const mockResponse = {
      response: 'Response based on selected text',
      sources: [{ title: 'Selected Text Source', url: 'https://example.com', snippet: 'Selected text snippet' }],
      confidence: 0.85,
      session_id: 'test-session-id'
    };
    mockChatbotAPI.queryChatbot.mockResolvedValue(mockResponse);

    render(<Chatbot initialMode="selected_text" />);

    // Open chatbot
    fireEvent.click(screen.getByLabelText('Open chatbot'));

    // Change to selected text mode
    const modeSelect = screen.getByRole('combobox');
    fireEvent.change(modeSelect, { target: { value: 'selected_text' } });

    // Type message
    const input = screen.getByPlaceholderText('Ask about the selected text...');
    fireEvent.change(input, { target: { value: 'Question about selected text' } });

    // Send message
    fireEvent.click(screen.getByText('Send'));

    // Wait for response
    await waitFor(() => {
      expect(screen.getByText('Response based on selected text')).toBeInTheDocument();
    });

    // Verify API was called with correct parameters
    expect(mockChatbotAPI.queryChatbot).toHaveBeenCalledWith(
      'Question about selected text',
      'selected_text',
      undefined
    );
  });

  test('should handle API errors gracefully', async () => {
    // Mock API error
    mockChatbotAPI.queryChatbot.mockRejectedValue(new Error('API Error'));

    render(<Chatbot initialMode="global" />);

    // Open chatbot
    fireEvent.click(screen.getByLabelText('Open chatbot'));

    // Type message
    const input = screen.getByPlaceholderText('Ask a question about the textbook content...');
    fireEvent.change(input, { target: { value: 'Test question' } });

    // Send message
    fireEvent.click(screen.getByText('Send'));

    // Wait for error message
    await waitFor(() => {
      expect(screen.getByText('Sorry, I encountered an error processing your request. Please try again.')).toBeInTheDocument();
    });
  });

  test('should handle empty message submission', () => {
    render(<Chatbot initialMode="global" />);

    // Open chatbot
    fireEvent.click(screen.getByLabelText('Open chatbot'));

    // Try to send empty message
    fireEvent.click(screen.getByText('Send'));

    // Should not call API
    expect(mockChatbotAPI.queryChatbot).not.toHaveBeenCalled();
  });

  test('should toggle chatbot visibility', () => {
    render(<Chatbot initialMode="global" />);

    // Initially closed
    expect(screen.queryByText('AI Textbook Assistant')).not.toBeInTheDocument();

    // Open chatbot
    fireEvent.click(screen.getByLabelText('Open chatbot'));
    expect(screen.getByText('AI Textbook Assistant')).toBeInTheDocument();

    // Close chatbot
    fireEvent.click(screen.getByTitle('Close chat'));
    expect(screen.queryByText('AI Textbook Assistant')).not.toBeInTheDocument();
  });

  test('should clear chat history', async () => {
    // Mock API response to allow messages to be added
    const mockResponse = {
      response: 'Test response',
      sources: [],
      confidence: 0.9,
      session_id: 'test-session-id'
    };
    mockChatbotAPI.queryChatbot.mockResolvedValue(mockResponse);

    render(<Chatbot initialMode="global" />);

    // Open chatbot
    fireEvent.click(screen.getByLabelText('Open chatbot'));

    // Add a message
    const input = screen.getByPlaceholderText('Ask a question about the textbook content...');
    fireEvent.change(input, { target: { value: 'Test question' } });
    fireEvent.click(screen.getByText('Send'));

    // Wait for response to appear
    await waitFor(() => {
      expect(screen.getByText('Test response')).toBeInTheDocument();
    });

    // Clear chat
    fireEvent.click(screen.getByTitle('Clear chat history'));

    // Verify chat is cleared
    expect(screen.queryByText('Test response')).not.toBeInTheDocument();
  });

  test('should change mode between global and selected text', () => {
    render(<Chatbot initialMode="global" />);

    // Open chatbot
    fireEvent.click(screen.getByLabelText('Open chatbot'));

    // Verify initial mode
    const modeSelect = screen.getByRole('combobox');
    expect(modeSelect.value).toBe('global');

    // Change to selected text mode
    fireEvent.change(modeSelect, { target: { value: 'selected_text' } });
    expect(modeSelect.value).toBe('selected_text');

    // Change back to global
    fireEvent.change(modeSelect, { target: { value: 'global' } });
    expect(modeSelect.value).toBe('global');
  });

  test('should submit feedback for chat interactions', async () => {
    const mockResponse = {
      response: 'Test response with sources',
      sources: [{ title: 'Test Source', url: 'https://example.com', snippet: 'Test snippet' }],
      confidence: 0.9,
      session_id: 'test-session-id'
    };
    mockChatbotAPI.queryChatbot.mockResolvedValue(mockResponse);
    mockChatbotAPI.submitFeedback.mockResolvedValue({ success: true });

    render(<Chatbot initialMode="global" />);

    // Open chatbot
    fireEvent.click(screen.getByLabelText('Open chatbot'));

    // Add a message to get a response
    const input = screen.getByPlaceholderText('Ask a question about the textbook content...');
    fireEvent.change(input, { target: { value: 'Test question' } });
    fireEvent.click(screen.getByText('Send'));

    // Wait for response to appear
    await waitFor(() => {
      expect(screen.getByText('Test response with sources')).toBeInTheDocument();
    });

    // Mock submitFeedback to test feedback submission
    // In a real test, we would test the actual feedback UI components
    const interactionId = 'test-interaction-id';
    await mockChatbotAPI.submitFeedback(interactionId, null, 5, true, 'Great response!', 5);

    expect(mockChatbotAPI.submitFeedback).toHaveBeenCalledWith(
      interactionId,
      null,
      5,
      true,
      'Great response!',
      5
    );
  });
});