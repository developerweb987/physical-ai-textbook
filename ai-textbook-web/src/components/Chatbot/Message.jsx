import React from 'react';

const Message = ({ message, mode }) => {
  const isUser = message.sender === 'user';

  return (
    <div className={`message ${isUser ? 'user-message' : 'bot-message'}`}>
      <div className="message-content">
        {isUser ? (
          <p>{message.content}</p>
        ) : (
          <>
            <p>{message.content}</p>
            {message.sources && message.sources.length > 0 && (
              <div className="message-sources">
                <details className="sources-details">
                  <summary>Sources</summary>
                  <ul>
                    {message.sources.map((source, index) => (
                      <li key={index}>
                        <a
                          href={source.url || '#'}
                          target="_blank"
                          rel="noopener noreferrer"
                          onClick={(e) => e.stopPropagation()}
                        >
                          {source.title || `Source ${index + 1}`}
                        </a>
                        {source.snippet && (
                          <p className="source-snippet">"{source.snippet}"</p>
                        )}
                      </li>
                    ))}
                  </ul>
                </details>
              </div>
            )}
            {message.confidence !== undefined && (
              <div className="message-confidence">
                <small>Confidence: {Math.round(message.confidence * 100)}%</small>
              </div>
            )}
            {message.isError && (
              <div className="message-error">
                <small className="error-text">⚠️ There was an error processing your request</small>
              </div>
            )}
          </>
        )}
      </div>
      <div className="message-timestamp">
        {message.timestamp ? message.timestamp.toLocaleTimeString() : ''}
      </div>
    </div>
  );
};

export default Message;