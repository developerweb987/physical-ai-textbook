from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, UUID, ARRAY, JSON
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime
import uuid

Base = declarative_base()

class StudentProfile(Base):
    __tablename__ = "student_profiles"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, nullable=False, unique=True)
    name = Column(String)  # Optional
    background = Column(String)  # Optional, student's technical background
    learning_preferences = Column(JSON)  # Optional, JSON object
    personalization_settings = Column(JSON)  # Optional, JSON object
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    last_active = Column(DateTime)  # Optional
    data_retention_until = Column(DateTime, nullable=False)  # Required, 2 years from last activity

    # Relationships
    chapter_progress = relationship("ChapterProgress", back_populates="student")
    chatbot_interactions = relationship("ChatbotInteraction", back_populates="student")
    chat_sessions = relationship("ChatSession", back_populates="student")
    chat_feedback = relationship("ChatFeedback", back_populates="student")