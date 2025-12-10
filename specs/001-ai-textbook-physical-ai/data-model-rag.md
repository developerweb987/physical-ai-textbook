# Data Model: RAG Chatbot for AI-Native Textbook

## Entities

### ChatbotInteraction
- **id**: UUID (primary key)
- **student_id**: UUID (foreign key to Student Profile, nullable for anonymous users)
- **query**: String (required) - The question asked by the user
- **response**: String (required) - The AI-generated response
- **context_mode**: Enum ['global', 'selected_text'] (required) - Whether using entire book or selected text
- **selected_text**: String (optional) - The text selected by user (for selected_text mode)
- **source_documents**: Array of document references (optional) - Citations for the response
- **timestamp**: DateTime (required) - When the interaction occurred
- **response_time_ms**: Integer (optional) - How long the response took
- **accuracy_score**: Float (0-1, optional) - Quality score for the response
- **session_id**: String (optional) - For conversation history
- **conversation_turn**: Integer (optional) - Position in conversation thread

### ChatSession
- **id**: String (primary key) - Session identifier
- **student_id**: UUID (foreign key to Student Profile, nullable for anonymous users)
- **started_at**: DateTime (required) - When session began
- **last_interaction**: DateTime (required) - Last activity in session
- **context_history**: Array of interaction summaries (optional) - Conversation history
- **context_length**: Integer (optional) - How many turns to keep in context
- **mode**: Enum ['global', 'selected_text'] (required) - Current mode for the session

### DocumentChunk
- **id**: String (primary key) - Unique identifier for the chunk
- **chapter_id**: UUID (foreign key to Textbook Chapter)
- **content**: String (required) - The text content of this chunk
- **chunk_index**: Integer (required) - Position of chunk within chapter
- **embedding_vector**: Array of floats (required) - Vector embedding of content
- **metadata**: JSON object (optional) - Additional metadata (page, section, etc.)
- **created_at**: DateTime (required)
- **updated_at**: DateTime (required)

### ChatFeedback
- **id**: UUID (primary key)
- **interaction_id**: UUID (foreign key to ChatbotInteraction)
- **student_id**: UUID (foreign key to Student Profile)
- **rating**: Integer (1-5) - Rating of response quality
- **feedback_text**: String (optional) - Additional feedback
- **helpful**: Boolean (optional) - Whether response was helpful
- **accuracy_rating**: Integer (1-5, optional) - Accuracy of information
- **timestamp**: DateTime (required)

## Relationships
- Student Profile (0..1) → (M) ChatbotInteractions
- ChatbotInteraction (1) → (0..1) ChatFeedback
- Textbook Chapter (1) → (M) DocumentChunks
- Student Profile (0..1) → (M) ChatSessions

## Validation Rules
- Queries must be between 5 and 2000 characters
- Responses must cite at least one source document when possible
- Accuracy scores must be between 0 and 1
- Context mode must be either 'global' or 'selected_text'
- Chat sessions expire after 30 minutes of inactivity

## State Transitions
- ChatSession: active → expired (based on inactivity timeout)
- ChatFeedback: pending → submitted (when feedback is provided)