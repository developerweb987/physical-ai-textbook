# Quickstart Guide: RAG Chatbot for AI-Native Textbook

## Prerequisites
- Python 3.11+
- OpenAI API key
- Qdrant vector database (local or cloud instance)
- Node.js 18+ for frontend components (if developing UI)

## Setup Instructions

### 1. Install Backend Dependencies
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Environment Configuration
Create `.env` file in the backend directory:

```env
OPENAI_API_KEY=your_openai_api_key
QDRANT_URL=your_qdrant_url
QDRANT_API_KEY=your_qdrant_api_key
DATABASE_URL=postgresql://user:password@localhost/ai_textbook
SECRET_KEY=your_secret_key
```

### 3. Initialize Vector Database
```bash
# Index textbook content for RAG functionality
cd backend
source venv/bin/activate
python -m api.rag.indexing
```

### 4. Start the Backend Service
```bash
cd backend
source venv/bin/activate
uvicorn api.main:app --reload --port 8000
```

## API Usage Examples

### 1. Query the Chatbot (Global Mode)
```bash
curl -X POST http://localhost:8000/api/v1/chatbot/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Explain the principles of bipedal locomotion in humanoid robots",
    "context_mode": "global"
  }'
```

### 2. Query the Chatbot (Selected Text Mode)
```bash
curl -X POST http://localhost:8000/api/v1/chatbot/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "How does this balance control work?",
    "context_mode": "selected_text",
    "selected_text": "Bipedal locomotion requires precise balance control using feedback from sensors like gyroscopes and accelerometers."
  }'
```

### 3. Create a Chat Session
```bash
curl -X POST http://localhost:8000/api/v1/chatbot/session \
  -H "Content-Type: application/json" \
  -d '{
    "context_mode": "global",
    "context_length": 5
  }'
```

### 4. Get Chat History
```bash
curl "http://localhost:8000/api/v1/chatbot/history?student_id=550e8400-e29b-41d4-a716-446655440000&limit=10"
```

## Frontend Integration

### 1. Install Chatbot Component
```bash
cd ai-textbook-web
npm install
```

### 2. Import and Use the Chatbot Component
```javascript
import { ChatbotInterface } from './src/components/Chatbot';

// Initialize the chatbot with API configuration
const chatbot = new ChatbotInterface({
  apiUrl: 'http://localhost:8000',
  contextMode: 'global'  // or 'selected_text'
});

// Handle user queries
const response = await chatbot.query(userQuestion);
```

## Content Indexing for RAG

### 1. Add New Content
When adding new textbook chapters, reindex the content:
```bash
python -m api.rag.indexing --full-reindex
```

### 2. Incremental Updates
For updates to specific chapters:
```bash
python -m api.rag.indexing --chapter-id CHAPTER_ID
```

## Testing the RAG Chatbot

### 1. Unit Tests
```bash
cd backend
source venv/bin/activate
pytest tests/unit/rag/
```

### 2. Integration Tests
```bash
cd backend
source venv/bin/activate
pytest tests/integration/rag/
```

### 3. Accuracy Validation
```bash
# Run accuracy tests against textbook content
python -m tests.integration.rag.accuracy_test
```

## Troubleshooting

- If chatbot responses are slow, check your OpenAI API key and Qdrant connection
- If queries return no results, verify content indexing completed successfully
- For context mode issues, ensure both global and selected-text modes are properly configured
- If citations are missing, check that document chunks contain proper source references

## Performance Optimization

- Adjust context window sizes based on conversation needs
- Implement caching for frequent queries
- Monitor response times and adjust as needed
- Use appropriate embedding models for your content type