import React from 'react';
import Message from './Message';

const ChatHistory = ({ messages, isLoading, mode }) => {
  if (messages.length === 0) {
    return (
      <div className="chat-history-empty">
        <p>No messages yet. Start a conversation with the AI assistant!</p>
      </div>
    );
  }

  return (
    <div className="chat-history">
      {messages.map((message) => (
        <Message
          key={message.id}
          message={message}
          mode={mode}
        />
      ))}
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
    </div>
  );
};

export default ChatHistory;