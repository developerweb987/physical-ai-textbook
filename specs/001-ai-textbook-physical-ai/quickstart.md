# Quickstart Guide: AI-Native Textbook for Physical AI & Humanoid Robotics

## Prerequisites
- Node.js 18+ and npm/yarn
- Python 3.11+ with pip
- Git
- OpenAI API key (for RAG chatbot)
- Qdrant vector database (local or cloud instance)

## Setup Instructions

### 1. Clone and Initialize the Textbook
```bash
# Clone the repository
git clone <repository-url>
cd ai-textbook-web

# Install frontend dependencies
npm install
# or
yarn install
```

### 2. Set Up Backend Services
```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install Python dependencies
pip install -r requirements.txt
```

### 3. Environment Configuration
Create `.env` files in both frontend and backend:

**Backend (.env):**
```env
OPENAI_API_KEY=your_openai_api_key
QDRANT_URL=your_qdrant_url
QDRANT_API_KEY=your_qdrant_api_key
DATABASE_URL=postgresql://user:password@localhost/dbname
SECRET_KEY=your_secret_key
```

**Frontend (.env):**
```env
REACT_APP_API_BASE_URL=http://localhost:8000
REACT_APP_OPENAI_API_KEY=your_openai_api_key  # Only if needed client-side
```

### 4. Database Setup
```bash
# Run database migrations
cd backend
source venv/bin/activate
alembic upgrade head
```

### 5. Content Indexing for RAG
```bash
# Index textbook content for chatbot
cd backend
source venv/bin/activate
python -m api.rag.indexing
```

### 6. Start Development Servers

**Backend:**
```bash
cd backend
source venv/bin/activate
uvicorn main:app --reload --port 8000
```

**Frontend:**
```bash
cd ai-textbook-web
npm start
# or
yarn start
```

## Adding New Content
1. Create new chapter files in `ai-textbook-web/docs/` directory
2. Add to navigation in `ai-textbook-web/sidebars.js`
3. Run content indexing: `python -m api.rag.indexing`
4. Test chapter accessibility and chatbot integration

## Testing the RAG Chatbot
1. Ensure backend server is running
2. Access the chatbot interface in the textbook
3. Test both global and selected-text modes
4. Verify responses are accurate and contextually appropriate

## Deployment to GitHub Pages
1. Build the static site: `npm run build`
2. The output will be in the `build/` directory
3. Configure GitHub Pages to serve from the `build/` directory
4. Ensure backend services are deployed separately

## Troubleshooting
- If chatbot responses are slow, check your OpenAI API key and Qdrant connection
- If pages don't load, verify the Docusaurus configuration
- For authentication issues, ensure your BetterAuth setup is complete
- For database errors, verify your PostgreSQL connection and run migrations