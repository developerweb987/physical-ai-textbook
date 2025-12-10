import React from 'react';

const ContextSelector = ({ mode, onModeChange, selectedText }) => {
  return (
    <div className="context-selector">
      <div className="context-mode-selector">
        <label htmlFor="context-mode">Context Mode:</label>
        <select
          id="context-mode"
          value={mode}
          onChange={(e) => onModeChange(e.target.value)}
          className="mode-select"
        >
          <option value="global">Global (Entire Book)</option>
          <option value="selected_text">Selected Text Only</option>
        </select>
      </div>

      {mode === 'selected_text' && selectedText && (
        <div className="selected-text-preview">
          <strong>Selected Text:</strong>
          <p>"{selectedText.substring(0, 150)}{selectedText.length > 150 ? '...' : ''}"</p>
        </div>
      )}

      <div className="context-info">
        <small>
          {mode === 'global'
            ? 'AI assistant will use the entire textbook content to answer your questions.'
            : 'AI assistant will only use the selected text to answer your questions.'}
        </small>
      </div>
    </div>
  );
};

export default ContextSelector;