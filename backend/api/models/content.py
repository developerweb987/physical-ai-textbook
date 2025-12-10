from sqlalchemy import Column, Integer, String, Text, DateTime, Float, Boolean, UUID, ForeignKey, ARRAY, JSON
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime
import uuid

Base = declarative_base()

class TextbookChapter(Base):
    __tablename__ = "textbook_chapters"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String, nullable=False)
    slug = Column(String, nullable=False, unique=True)
    content = Column(Text, nullable=False)  # Markdown content
    learning_outcomes = Column(ARRAY(String), nullable=False)
    diagrams = Column(ARRAY(String))  # Array of diagram references
    code_examples = Column(ARRAY(Text))  # Array of code blocks
    exercises = Column(ARRAY(Text))  # Array of exercise objects
    chapter_number = Column(Integer, nullable=False, unique=True)  # Unique per textbook
    prerequisites = Column(ARRAY(PG_UUID))  # Array of chapter IDs
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    status = Column(String, default='draft', nullable=False)  # draft, review, published

class ChapterProgress(Base):
    __tablename__ = "chapter_progress"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    student_id = Column(PG_UUID(as_uuid=True), ForeignKey("student_profiles.id"), nullable=False)
    chapter_id = Column(PG_UUID(as_uuid=True), ForeignKey("textbook_chapters.id"), nullable=False)
    completion_percentage = Column(Float, nullable=False)  # 0-100
    time_spent_seconds = Column(Integer)  # Optional
    last_accessed = Column(DateTime)  # Optional
    exercises_completed = Column(ARRAY(String))  # Array of exercise IDs
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    student = relationship("StudentProfile", back_populates="chapter_progress")
    chapter = relationship("TextbookChapter")

class ChatbotInteraction(Base):
    __tablename__ = "chatbot_interactions"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    student_id = Column(PG_UUID(as_uuid=True), ForeignKey("student_profiles.id"), nullable=True)  # Nullable for anonymous users
    query = Column(String, nullable=False)
    response = Column(String, nullable=False)
    context_mode = Column(String, nullable=False)  # 'global' or 'selected_text'
    selected_text = Column(Text)  # Optional, for selected_text mode
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    response_time_ms = Column(Integer)  # Optional
    accuracy_score = Column(Float)  # 0-1, optional for quality tracking
    sources = Column(ARRAY(String))  # Array of source document references

class ChatSession(Base):
    __tablename__ = "chat_sessions"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    student_id = Column(PG_UUID(as_uuid=True), ForeignKey("student_profiles.id"), nullable=True)
    started_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_interaction = Column(DateTime, default=datetime.utcnow, nullable=False)
    context_length = Column(Integer, default=5)  # Number of previous turns to maintain
    context_mode = Column(String, default='global', nullable=False)  # 'global' or 'selected_text'

class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    chapter_id = Column(PG_UUID(as_uuid=True), ForeignKey("textbook_chapters.id"), nullable=False)
    content = Column(Text, nullable=False)
    chunk_index = Column(Integer, nullable=False)  # Position of chunk within chapter
    embedding_vector = Column(String)  # Store as JSON string or use a vector extension if available
    metadata = Column(JSON)  # Additional metadata (section, page, etc.)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

class ChatFeedback(Base):
    __tablename__ = "chat_feedback"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    interaction_id = Column(PG_UUID(as_uuid=True), ForeignKey("chatbot_interactions.id"), nullable=False)
    student_id = Column(PG_UUID(as_uuid=True), ForeignKey("student_profiles.id"), nullable=True)
    rating = Column(Integer)  # 1-5 rating
    helpful = Column(Boolean)  # Whether response was helpful
    feedback_text = Column(Text)  # Additional feedback
    accuracy_rating = Column(Integer)  # 1-5 rating of accuracy
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)