// ai-textbook-web/src/services/chatbot-api.js

class ChatbotAPI {
  constructor(baseURL = '/api/v1') {
    this.baseURL = baseURL;
  }

  async queryChatbot(query, contextMode, selectedText = null, sessionId = null, studentId = null) {
    const requestBody = {
      query,
      context_mode: contextMode,
    };

    if (contextMode === 'selected_text' && selectedText) {
      requestBody.selected_text = selectedText;
    }

    if (sessionId) {
      requestBody.session_id = sessionId;
    }

    if (studentId) {
      requestBody.student_id = studentId;
    }

    try {
      const response = await fetch(`${this.baseURL}/chatbot/query`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestBody)
      });

      if (!response.ok) {
        throw new Error(`Chatbot API error: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error calling chatbot API:', error);
      throw error;
    }
  }

  async createSession(studentId = null, contextMode = 'global', contextLength = 5) {
    const requestBody = {
      student_id: studentId,
      context_mode: contextMode,
      context_length: contextLength,
    };

    try {
      const response = await fetch(`${this.baseURL}/chatbot/session`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestBody)
      });

      if (!response.ok) {
        throw new Error(`Session creation error: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error creating chat session:', error);
      throw error;
    }
  }

  async getChatHistory(studentId = null, sessionId = null, limit = 10) {
    let url = `${this.baseURL}/chatbot/history?limit=${limit}`;

    if (studentId) {
      url += `&student_id=${studentId}`;
    }

    if (sessionId) {
      url += `&session_id=${sessionId}`;
    }

    try {
      const response = await fetch(url, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        }
      });

      if (!response.ok) {
        throw new Error(`Chat history error: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error fetching chat history:', error);
      throw error;
    }
  }

  async submitFeedback(interactionId, studentId = null, rating = null, helpful = null, feedbackText = null, accuracyRating = null) {
    const requestBody = {
      interaction_id: interactionId,
      student_id: studentId,
      rating,
      helpful,
      feedback_text: feedbackText,
      accuracy_rating: accuracyRating,
    };

    try {
      const response = await fetch(`${this.baseURL}/chatbot/feedback`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestBody)
      });

      if (!response.ok) {
        throw new Error(`Feedback submission error: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error submitting feedback:', error);
      throw error;
    }
  }
}

export default ChatbotAPI;