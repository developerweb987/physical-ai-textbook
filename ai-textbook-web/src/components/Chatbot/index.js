import React, { useState, useRef, useEffect } from 'react';
import ChatInterface from './ChatInterface';
import ChatbotAPI from '../../services/chatbot-api';
import './Chatbot.css';

const Chatbot = ({ initialMode = 'global' }) => {
  const [isOpen, setIsOpen] = useState(false);
  const [mode, setMode] = useState(initialMode);
  const [selectedText, setSelectedText] = useState('');
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);

  const chatContainerRef = useRef(null);

  // Toggle chatbot visibility
  const toggleChatbot = () => {
    setIsOpen(!isOpen);
  };

  // Initialize chatbot API
  const chatbotAPI = new ChatbotAPI();

  // Handle sending a message
  const handleSendMessage = async (message) => {
    if (!message.trim() || isLoading) return;

    // Add user message to chat
    const userMessage = {
      id: Date.now(),
      sender: 'user',
      content: message,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setIsLoading(true);

    try {
      // Call the backend API using the client
      const data = await chatbotAPI.queryChatbot(message, mode, selectedText);

      // Add bot response to chat
      const botMessage = {
        id: Date.now() + 1,
        sender: 'bot',
        content: data.response,
        sources: data.sources,
        confidence: data.confidence,
        timestamp: new Date()
      };

      setMessages(prev => [...prev, botMessage]);
    } catch (error) {
      console.error('Error sending message to chatbot:', error);

      // Add error message to chat
      const errorMessage = {
        id: Date.now() + 1,
        sender: 'bot',
        content: 'Sorry, I encountered an error processing your request. Please try again.',
        isError: true,
        timestamp: new Date()
      };

      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  // Handle mode change
  const handleModeChange = (newMode) => {
    setMode(newMode);
  };

  // Handle text selection
  const handleTextSelected = (selectedText) => {
    setSelectedText(selectedText);
  };

  // Clear chat history
  const handleClearChat = () => {
    setMessages([]);
  };

  return (
    <>
      {!isOpen ? (
        <button
          className="chatbot-toggle-button"
          onClick={toggleChatbot}
          aria-label="Open chatbot"
        >
          💬 AI Assistant
        </button>
      ) : (
        <div className="chatbot-container">
          <div className="chatbot-header">
            <h3>AI Textbook Assistant</h3>
            <div className="chatbot-controls">
              <select
                value={mode}
                onChange={(e) => setMode(e.target.value)}
                className="mode-selector"
              >
                <option value="global">Global (Entire Book)</option>
                <option value="selected_text">Selected Text Only</option>
              </select>
              <button
                onClick={handleClearChat}
                className="clear-chat-button"
                title="Clear chat history"
              >
                🗑️
              </button>
              <button
                onClick={toggleChatbot}
                className="close-chat-button"
                title="Close chat"
              >
                ×
              </button>
            </div>
          </div>

          <ChatInterface
            messages={messages}
            onSendMessage={handleSendMessage}
            isLoading={isLoading}
            mode={mode}
            selectedText={selectedText}
          />
        </div>
      )}
    </>
  );
};

export default Chatbot;