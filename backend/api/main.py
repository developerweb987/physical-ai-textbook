from fastapi import FastAPI, Request, HTTPException, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
import logging
from datetime import datetime
import traceback
from typing import Dict, Any, List, Optional
from pydantic import BaseModel
import uuid
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from .models.content import TextbookChapter, ChapterProgress, ChatbotInteraction, ChatSession, ChatFeedback
from .models.user import StudentProfile
from .services.content_management import ChapterService
from .services.rag_service import RAGService, ContextMode
from .rag.chatbot import RAGChatbotService, ChatResponse
from .rag.retrieval import SimilarityRetriever
from .rag.embedding import EmbeddingService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database setup (this would normally be in a separate config file)
DATABASE_URL = "sqlite:///./ai_textbook.db"  # Default for development
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Create the FastAPI app
app = FastAPI(
    title="AI Textbook API",
    description="API for the AI-Native Textbook for Physical AI & Humanoid Robotics",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Custom exception handler for validation errors
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.error(f"Validation error: {exc}")
    return JSONResponse(
        status_code=422,
        content={
            "detail": "Validation error",
            "errors": [
                {
                    "loc": error["loc"],
                    "msg": error["msg"],
                    "type": error["type"],
                }
                for error in exc.errors()
            ],
            "timestamp": datetime.utcnow().isoformat()
        }
    )

# General exception handler
@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unexpected error: {exc}\n{traceback.format_exc()}")
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "timestamp": datetime.utcnow().isoformat()
        }
    )

@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Middleware to log all incoming requests"""
    start_time = datetime.utcnow()
    response = await call_next(request)
    process_time = (datetime.utcnow() - start_time).total_seconds()

    logger.info(f"{request.method} {request.url.path} - Status: {response.status_code} - Process time: {process_time}s")

    return response

@app.get("/")
async def root():
    return {"message": "AI Textbook API is running!"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# Pydantic models for request/response validation
class ChapterResponse(BaseModel):
    id: uuid.UUID
    title: str
    slug: str
    content: str
    learning_outcomes: List[str]
    diagrams: List[str]
    code_examples: List[str]
    exercises: List[str]
    chapter_number: int
    prerequisites: List[uuid.UUID]
    created_at: datetime
    updated_at: datetime
    status: str

    class Config:
        from_attributes = True

class ChapterCreateRequest(BaseModel):
    title: str
    slug: str
    content: str
    learning_outcomes: List[str]
    diagrams: Optional[List[str]] = []
    code_examples: Optional[List[str]] = []
    exercises: Optional[List[str]] = []
    chapter_number: int
    prerequisites: Optional[List[uuid.UUID]] = []

class ChapterUpdateRequest(BaseModel):
    title: Optional[str] = None
    slug: Optional[str] = None
    content: Optional[str] = None
    learning_outcomes: Optional[List[str]] = None
    diagrams: Optional[List[str]] = None
    code_examples: Optional[List[str]] = None
    exercises: Optional[List[str]] = None
    chapter_number: Optional[int] = None
    prerequisites: Optional[List[uuid.UUID]] = None
    status: Optional[str] = None

class ChapterProgressRequest(BaseModel):
    completion_percentage: float
    exercises_completed: Optional[List[str]] = []
    time_spent_seconds: Optional[int] = None

class ChapterProgressResponse(BaseModel):
    id: uuid.UUID
    student_id: uuid.UUID
    chapter_id: uuid.UUID
    completion_percentage: float
    time_spent_seconds: Optional[int]
    last_accessed: Optional[datetime]
    exercises_completed: List[str]
    created_at: datetime
    updated_at: datetime

# Chatbot-related models
class ChatbotQueryRequest(BaseModel):
    query: str
    context_mode: str  # 'global' or 'selected_text'
    selected_text: Optional[str] = None  # Required if context_mode is 'selected_text'
    student_id: Optional[uuid.UUID] = None
    session_id: Optional[str] = None

class ChatbotResponse(BaseModel):
    response: str
    sources: List[Dict[str, Any]]
    confidence: float
    session_id: Optional[str] = None
    response_time_ms: Optional[int] = None

class ChatSessionCreateRequest(BaseModel):
    student_id: Optional[uuid.UUID] = None
    context_mode: Optional[str] = "global"  # 'global' or 'selected_text'
    context_length: Optional[int] = 5

class ChatSessionResponse(BaseModel):
    session_id: str
    created_at: datetime
    context_mode: str

class ChatHistoryResponse(BaseModel):
    id: uuid.UUID
    query: str
    response: str
    timestamp: datetime
    context_mode: str
    session_id: str

class ChatFeedbackRequest(BaseModel):
    interaction_id: uuid.UUID
    student_id: Optional[uuid.UUID] = None
    rating: Optional[int] = None  # 1-5 rating
    helpful: Optional[bool] = None
    feedback_text: Optional[str] = None
    accuracy_rating: Optional[int] = None  # 1-5 rating of accuracy

# Chapter endpoints
@app.get("/api/v1/chapters", response_model=List[ChapterResponse])
async def get_chapters(
    status: Optional[str] = Query(None, description="Filter by status (draft, review, published)"),
    db: Session = Depends(get_db)
):
    """Get all textbook chapters with optional status filter."""
    service = ChapterService(db)
    chapters = service.get_all_chapters(status=status)
    return chapters

@app.get("/api/v1/chapters/{chapter_id}", response_model=ChapterResponse)
async def get_chapter(chapter_id: uuid.UUID, db: Session = Depends(get_db)):
    """Get a specific textbook chapter by ID."""
    service = ChapterService(db)
    chapter = service.get_chapter_by_id(chapter_id)
    if not chapter:
        raise HTTPException(status_code=404, detail="Chapter not found")
    return chapter

@app.get("/api/v1/chapters/slug/{slug}", response_model=ChapterResponse)
async def get_chapter_by_slug(slug: str, db: Session = Depends(get_db)):
    """Get a specific textbook chapter by slug."""
    service = ChapterService(db)
    chapter = service.get_chapter_by_slug(slug)
    if not chapter:
        raise HTTPException(status_code=404, detail="Chapter not found")
    return chapter

@app.post("/api/v1/chapters", response_model=ChapterResponse)
async def create_chapter(chapter_data: ChapterCreateRequest, db: Session = Depends(get_db)):
    """Create a new textbook chapter."""
    service = ChapterService(db)

    # Check if slug or chapter number already exists
    existing_by_slug = service.get_chapter_by_slug(chapter_data.slug)
    existing_by_number = db.query(TextbookChapter).filter(
        TextbookChapter.chapter_number == chapter_data.chapter_number
    ).first()

    if existing_by_slug:
        raise HTTPException(status_code=400, detail="Chapter with this slug already exists")
    if existing_by_number:
        raise HTTPException(status_code=400, detail="Chapter with this number already exists")

    chapter = service.create_chapter(
        title=chapter_data.title,
        slug=chapter_data.slug,
        content=chapter_data.content,
        learning_outcomes=chapter_data.learning_outcomes,
        diagrams=chapter_data.diagrams,
        code_examples=chapter_data.code_examples,
        exercises=chapter_data.exercises,
        chapter_number=chapter_data.chapter_number,
        prerequisites=chapter_data.prerequisites
    )
    return chapter

@app.put("/api/v1/chapters/{chapter_id}", response_model=ChapterResponse)
async def update_chapter(chapter_id: uuid.UUID, chapter_data: ChapterUpdateRequest, db: Session = Depends(get_db)):
    """Update an existing textbook chapter."""
    service = ChapterService(db)
    chapter = service.get_chapter_by_id(chapter_id)
    if not chapter:
        raise HTTPException(status_code=404, detail="Chapter not found")

    # Update fields if provided
    if chapter_data.title is not None:
        chapter.title = chapter_data.title
    if chapter_data.slug is not None:
        # Check if slug already exists for another chapter
        existing = service.get_chapter_by_slug(chapter_data.slug)
        if existing and existing.id != chapter_id:
            raise HTTPException(status_code=400, detail="Chapter with this slug already exists")
        chapter.slug = chapter_data.slug
    if chapter_data.content is not None:
        chapter.content = chapter_data.content
    if chapter_data.learning_outcomes is not None:
        chapter.learning_outcomes = chapter_data.learning_outcomes
    if chapter_data.diagrams is not None:
        chapter.diagrams = chapter_data.diagrams
    if chapter_data.code_examples is not None:
        chapter.code_examples = chapter_data.code_examples
    if chapter_data.exercises is not None:
        chapter.exercises = chapter_data.exercises
    if chapter_data.chapter_number is not None:
        # Check if chapter number already exists for another chapter
        existing = db.query(TextbookChapter).filter(
            TextbookChapter.chapter_number == chapter_data.chapter_number
        ).first()
        if existing and existing.id != chapter_id:
            raise HTTPException(status_code=400, detail="Chapter with this number already exists")
        chapter.chapter_number = chapter_data.chapter_number
    if chapter_data.prerequisites is not None:
        chapter.prerequisites = chapter_data.prerequisites
    if chapter_data.status is not None:
        chapter.status = chapter_data.status

    db.commit()
    db.refresh(chapter)
    return chapter

@app.post("/api/v1/chapters/{chapter_id}/progress", response_model=ChapterProgressResponse)
async def update_chapter_progress(
    chapter_id: uuid.UUID,
    progress_data: ChapterProgressRequest,
    student_id: uuid.UUID,
    db: Session = Depends(get_db)
):
    """Update a student's progress for a specific chapter."""
    service = ChapterService(db)

    # Validate chapter exists
    chapter = service.get_chapter_by_id(chapter_id)
    if not chapter:
        raise HTTPException(status_code=404, detail="Chapter not found")

    # Validate student exists
    student = db.query(StudentProfile).filter(StudentProfile.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    # Validate completion percentage
    if progress_data.completion_percentage < 0 or progress_data.completion_percentage > 100:
        raise HTTPException(status_code=400, detail="Completion percentage must be between 0 and 100")

    progress = service.update_chapter_progress(
        student_id=student_id,
        chapter_id=chapter_id,
        completion_percentage=progress_data.completion_percentage,
        exercises_completed=progress_data.exercises_completed,
        time_spent_seconds=progress_data.time_spent_seconds
    )
    return progress

# RAG Chatbot endpoints
@app.post("/api/v1/chatbot/query", response_model=ChatbotResponse)
async def chatbot_query(
    query_data: ChatbotQueryRequest,
    db: Session = Depends(get_db)
):
    """Submit a query to the RAG chatbot with support for both global and selected-text modes."""
    try:
        # Initialize RAG chatbot service (in a real implementation, this would be configured properly)
        # For now, we'll simulate the service
        from qdrant_client import QdrantClient

        # These would normally be configured in environment variables
        openai_api_key = "fake-key-for-now"  # This should come from env
        qdrant_url = "http://localhost:6333"  # This should come from env
        qdrant_api_key = "fake-key-for-now"  # This should come from env

        # Initialize services (these would be properly configured in a real implementation)
        # For now, we'll simulate the service
        from qdrant_client import QdrantClient
        from .rag.embedding import EmbeddingService
        from .rag.retrieval import SimilarityRetriever
        from .services.rag_service import RAGService, ContextMode
        from .rag.chatbot import RAGChatbotService

        import os

        # These would normally be configured in environment variables
        openai_api_key = os.getenv("OPENAI_API_KEY", "fake-key-for-now")  # This should come from env
        qdrant_url = os.getenv("QDRANT_URL", "http://localhost:6333")  # This should come from env
        qdrant_api_key = os.getenv("QDRANT_API_KEY", "fake-key-for-now")  # This should come from env

        # Initialize services
        embedding_service = EmbeddingService(openai_api_key=openai_api_key)
        qdrant_client = QdrantClient(url=qdrant_url, api_key=qdrant_api_key)
        retriever = SimilarityRetriever(qdrant_client, embedding_service)
        rag_service = RAGService(retriever, embedding_service, db)

        # Create or use existing session
        session_id = query_data.session_id
        if not session_id:
            session_id = await rag_service.create_session(
                student_id=str(query_data.student_id) if query_data.student_id else None,
                context_mode=ContextMode(query_data.context_mode)
            )

        # Validate context mode
        if query_data.context_mode not in ["global", "selected_text"]:
            raise HTTPException(status_code=400, detail="context_mode must be 'global' or 'selected_text'")

        # For selected_text mode, selected_text is required
        if query_data.context_mode == "selected_text" and not query_data.selected_text:
            raise HTTPException(status_code=400, detail="selected_text is required when context_mode is 'selected_text'")

        # Call the RAG chatbot service
        context_mode_enum = ContextMode.GLOBAL if query_data.context_mode == "global" else ContextMode.SELECTED_TEXT

        start_time = datetime.utcnow()
        chatbot_service = RAGChatbotService(
            openai_api_key=openai_api_key,
            qdrant_url=qdrant_url,
            qdrant_api_key=qdrant_api_key
        )
        response = await chatbot_service.query(
            query=query_data.query,
            context_mode=context_mode_enum,
            session_id=session_id,
            selected_text=query_data.selected_text,
            student_id=str(query_data.student_id) if query_data.student_id else None
        )
        response_time = (datetime.utcnow() - start_time).total_seconds() * 1000  # Convert to milliseconds

        return ChatbotResponse(
            response=response.response,
            sources=response.sources,
            confidence=response.confidence,
            session_id=response.session_id,
            response_time_ms=int(response_time)
        )
    except Exception as e:
        logger.error(f"Error processing chatbot query: {e}")
        raise HTTPException(status_code=500, detail="Error processing chatbot query")

@app.post("/api/v1/chatbot/session", response_model=ChatSessionResponse)
async def create_chat_session(
    session_data: ChatSessionCreateRequest,
    db: Session = Depends(get_db)
):
    """Create a new chat session with specified context mode."""
    try:
        # Initialize RAG service (similar to above)
        from qdrant_client import QdrantClient
        from .services.rag_service import ContextMode

        # These would normally be configured in environment variables
        openai_api_key = "fake-key-for-now"  # This should come from env
        qdrant_url = "http://localhost:6333"  # This should come from env
        qdrant_api_key = "fake-key-for-now"  # This should come from env

        # Initialize services
        embedding_service = EmbeddingService(openai_api_key=openai_api_key)
        qdrant_client = QdrantClient(url=qdrant_url, api_key=qdrant_api_key)
        retriever = SimilarityRetriever(qdrant_client, embedding_service)
        rag_service = RAGService(retriever, embedding_service, db)

        # Validate context mode
        if session_data.context_mode not in ["global", "selected_text"]:
            raise HTTPException(status_code=400, detail="context_mode must be 'global' or 'selected_text'")

        context_mode_enum = ContextMode.GLOBAL if session_data.context_mode == "global" else ContextMode.SELECTED_TEXT

        session_id = await rag_service.create_session(
            student_id=str(session_data.student_id) if session_data.student_id else None,
            context_mode=context_mode_enum,
            context_length=session_data.context_length
        )

        # Get the session to return details
        session = await rag_service.get_session(session_id)

        return ChatSessionResponse(
            session_id=session_id,
            created_at=session.started_at,
            context_mode=session.context_mode
        )
    except Exception as e:
        logger.error(f"Error creating chat session: {e}")
        raise HTTPException(status_code=500, detail="Error creating chat session")

@app.get("/api/v1/chatbot/history", response_model=List[ChatHistoryResponse])
async def get_chat_history(
    student_id: Optional[uuid.UUID] = None,
    session_id: Optional[str] = None,
    limit: int = Query(default=10, ge=1, le=50),
    db: Session = Depends(get_db)
):
    """Get chat history for a student or session."""
    try:
        # Query the database for chatbot interactions
        query = db.query(ChatbotInteraction)

        if student_id:
            query = query.filter(ChatbotInteraction.student_id == student_id)
        if session_id:
            query = query.filter(ChatbotInteraction.session_id == session_id)

        interactions = query.order_by(ChatbotInteraction.timestamp.desc()).limit(limit).all()

        history = []
        for interaction in interactions:
            history_item = ChatHistoryResponse(
                id=interaction.id,
                query=interaction.query,
                response=interaction.response,
                timestamp=interaction.timestamp,
                context_mode=interaction.context_mode,
                session_id=interaction.session_id
            )
            history.append(history_item)

        # Reverse to show in chronological order (oldest first)
        return list(reversed(history))
    except Exception as e:
        logger.error(f"Error retrieving chat history: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving chat history")

@app.post("/api/v1/chatbot/feedback")
async def submit_chat_feedback(
    feedback_data: ChatFeedbackRequest,
    db: Session = Depends(get_db)
):
    """Submit feedback for a chat interaction."""
    try:
        # Validate that the interaction exists
        interaction = db.query(ChatbotInteraction).filter(
            ChatbotInteraction.id == feedback_data.interaction_id
        ).first()

        if not interaction:
            raise HTTPException(status_code=404, detail="Chat interaction not found")

        # Create feedback record
        feedback = ChatFeedback(
            id=uuid.uuid4(),
            interaction_id=feedback_data.interaction_id,
            student_id=feedback_data.student_id,
            rating=feedback_data.rating,
            helpful=feedback_data.helpful,
            feedback_text=feedback_data.feedback_text,
            accuracy_rating=feedback_data.accuracy_rating
        )

        db.add(feedback)
        db.commit()

        return {"success": True, "message": "Feedback submitted successfully"}
    except Exception as e:
        logger.error(f"Error submitting chat feedback: {e}")
        raise HTTPException(status_code=500, detail="Error submitting chat feedback")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)