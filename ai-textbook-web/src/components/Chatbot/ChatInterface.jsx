import React, { useState, useEffect, useRef } from 'react';
import Message from './Message';
import './ChatInterface.css';

const ChatInterface = ({ messages, onSendMessage, isLoading, mode, selectedText }) => {
  const [inputText, setInputText] = useState('');
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  // Scroll to bottom of messages when new messages arrive
  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (inputText.trim() && !isLoading) {
      onSendMessage(inputText);
      setInputText('');
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  return (
    <div className="chat-interface">
      <div className="chat-messages">
        {messages.length === 0 ? (
          <div className="welcome-message">
            <h4>Welcome to the AI Textbook Assistant!</h4>
            <p>
              {mode === 'global'
                ? 'Ask me anything about the textbook content. I can help with concepts, examples, and exercises from the entire book.'
                : 'Ask me about the selected text. I can provide explanations based only on the text you have selected.'}
            </p>
            {selectedText && (
              <div className="selected-text-preview">
                <strong>Selected Text:</strong>
                <p>"{selectedText.substring(0, 100)}{selectedText.length > 100 ? '...' : ''}"</p>
              </div>
            )}
          </div>
        ) : (
          messages.map((message) => (
            <Message
              key={message.id}
              message={message}
              mode={mode}
            />
          ))
        )}
        {isLoading && (
          <div className="message bot-message">
            <div className="message-content">
              <div className="typing-indicator">
                <span></span>
                <span></span>
                <span></span>
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      <form className="chat-input-form" onSubmit={handleSubmit}>
        <div className="input-container">
          <textarea
            ref={inputRef}
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder={
              mode === 'global'
                ? 'Ask a question about the textbook content...'
                : 'Ask about the selected text...'
            }
            disabled={isLoading}
            rows={1}
            className="chat-input"
          />
          <button
            type="submit"
            disabled={!inputText.trim() || isLoading}
            className="send-button"
          >
            {isLoading ? 'Sending...' : 'Send'}
          </button>
        </div>
        <div className="input-hints">
          <small>
            Press Enter to send, Shift+Enter for new line • Mode: {mode === 'global' ? 'Global' : 'Selected Text Only'}
          </small>
        </div>
      </form>
    </div>
  );
};

export default ChatInterface;