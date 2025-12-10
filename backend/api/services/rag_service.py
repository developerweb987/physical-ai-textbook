import asyncio
import logging
from typing import List, Dict, Optional, Tuple, Any
from datetime import datetime, timedelta
from enum import Enum
import uuid
from dataclasses import dataclass

from sqlalchemy.orm import Session
from sqlalchemy import func

from ..models.content import ChatSession, ChatbotInteraction, ChatFeedback
from ..database import SessionLocal
from ..rag.retrieval import SimilarityRetriever, RetrievedChunk
from ..rag.embedding import EmbeddingService

logger = logging.getLogger(__name__)

class ContextMode(str, Enum):
    GLOBAL = "global"
    SELECTED_TEXT = "selected_text"

@dataclass
class ChatResponse:
    """Response from the chatbot service."""
    response: str
    sources: List[Dict[str, Any]]
    confidence: float
    session_id: Optional[str] = None
    response_time_ms: Optional[int] = None

@dataclass
class ValidationResult:
    """Result of response validation."""
    is_valid: bool
    confidence_score: float
    citations: List[Dict[str, str]]
    feedback: str

class RAGService:
    """
    Service for managing RAG (Retrieval-Augmented Generation) operations including
    session management, response validation, and citation generation.
    """

    def __init__(
        self,
        similarity_retriever: SimilarityRetriever,
        embedding_service: EmbeddingService,
        db_session: Session
    ):
        self.retriever = similarity_retriever
        self.embedding_service = embedding_service
        self.db = db_session

    async def create_session(
        self,
        student_id: Optional[str] = None,
        context_mode: ContextMode = ContextMode.GLOBAL,
        context_length: int = 5
    ) -> str:
        """
        Create a new chat session.

        Args:
            student_id: Optional student identifier
            context_mode: Initial context mode for the session
            context_length: Number of previous turns to maintain in context

        Returns:
            Session ID for the created session
        """
        try:
            session = ChatSession(
                id=str(uuid.uuid4()),
                student_id=student_id,
                started_at=datetime.utcnow(),
                last_interaction=datetime.utcnow(),
                context_length=context_length,
                context_mode=context_mode.value
            )

            self.db.add(session)
            self.db.commit()
            self.db.refresh(session)

            logger.info(f"Created new chat session: {session.id}")
            return session.id

        except Exception as e:
            logger.error(f"Error creating chat session: {e}")
            self.db.rollback()
            raise

    async def get_session(self, session_id: str) -> Optional[ChatSession]:
        """
        Retrieve an existing chat session.

        Args:
            session_id: The session identifier

        Returns:
            ChatSession object if found, None otherwise
        """
        try:
            session = self.db.query(ChatSession).filter(ChatSession.id == session_id).first()
            if session:
                # Update last interaction time
                session.last_interaction = datetime.utcnow()
                self.db.commit()
            return session
        except Exception as e:
            logger.error(f"Error retrieving chat session {session_id}: {e}")
            return None

    async def get_conversation_context(
        self,
        session_id: str,
        turn_count: int = 3
    ) -> List[Dict[str, str]]:
        """
        Retrieve conversation history for context.

        Args:
            session_id: The session identifier
            turn_count: Number of previous turns to retrieve

        Returns:
            List of conversation turns (query-response pairs)
        """
        try:
            # Get recent interactions for this session
            recent_interactions = (
                self.db.query(ChatbotInteraction)
                .filter(ChatbotInteraction.session_id == session_id)
                .order_by(ChatbotInteraction.timestamp.desc())
                .limit(turn_count)
                .all()
            )

            # Convert to context format (reverse order to get chronological sequence)
            context = []
            for interaction in reversed(recent_interactions):
                context.append({
                    "query": interaction.query,
                    "response": interaction.response
                })

            logger.debug(f"Retrieved {len(context)} turns of context for session {session_id}")
            return context

        except Exception as e:
            logger.error(f"Error retrieving conversation context for session {session_id}: {e}")
            return []

    async def validate_response(
        self,
        query: str,
        response: str,
        retrieved_chunks: List[RetrievedChunk],
        threshold: float = 0.7
    ) -> ValidationResult:
        """
        Validate the response for accuracy and relevance.

        Args:
            query: The original query
            response: The generated response
            retrieved_chunks: The chunks used to generate the response
            threshold: Minimum confidence threshold for validity

        Returns:
            ValidationResult indicating validity and confidence
        """
        try:
            # Calculate confidence based on:
            # 1. Average relevance score of retrieved chunks
            # 2. Proportion of response that can be attributed to sources
            # 3. Semantic similarity between query and response

            if not retrieved_chunks:
                return ValidationResult(
                    is_valid=False,
                    confidence_score=0.0,
                    citations=[],
                    feedback="No sources used for response generation"
                )

            # Calculate average relevance score
            avg_relevance = sum(chunk.score for chunk in retrieved_chunks) / len(retrieved_chunks)

            # Generate embeddings for semantic similarity check
            query_embedding = await self.embedding_service.generate_embedding(query)
            response_embedding = await self.embedding_service.generate_embedding(response)

            # Calculate similarity between query and response
            response_relevance = self.embedding_service.calculate_similarity(
                query_embedding,
                response_embedding
            )

            # Weighted confidence score
            confidence_score = (avg_relevance * 0.6) + (response_relevance * 0.4)

            # Generate citations from retrieved chunks
            citations = []
            for chunk in retrieved_chunks:
                citations.append({
                    "content_snippet": chunk.content[:200] + "..." if len(chunk.content) > 200 else chunk.content,
                    "source": chunk.source,
                    "relevance_score": chunk.score,
                    "metadata": chunk.metadata
                })

            # Determine validity based on threshold
            is_valid = confidence_score >= threshold

            validation_result = ValidationResult(
                is_valid=is_valid,
                confidence_score=confidence_score,
                citations=citations,
                feedback=f"Response validated with confidence {confidence_score:.2f}" if is_valid
                         else f"Response below threshold ({threshold}), confidence {confidence_score:.2f}"
            )

            logger.debug(f"Response validation result: {validation_result.feedback}")
            return validation_result

        except Exception as e:
            logger.error(f"Error validating response: {e}")
            return ValidationResult(
                is_valid=False,
                confidence_score=0.0,
                citations=[],
                feedback=f"Validation failed due to error: {str(e)}"
            )

    async def generate_citations(
        self,
        retrieved_chunks: List[RetrievedChunk]
    ) -> List[Dict[str, str]]:
        """
        Generate proper citations for the retrieved content used in the response.

        Args:
            retrieved_chunks: List of retrieved chunks used in the response

        Returns:
            List of citation objects with source information
        """
        citations = []
        for chunk in retrieved_chunks:
            # Extract source information from metadata
            source_info = {
                "title": chunk.metadata.get("chapter_title", "Unknown Chapter"),
                "chapter_number": chunk.metadata.get("chapter_number", "N/A"),
                "section": chunk.metadata.get("section", "General"),
                "content_snippet": chunk.content[:150] + "..." if len(chunk.content) > 150 else chunk.content,
                "source_document": chunk.source,
                "relevance_score": f"{chunk.score:.2f}"
            }
            citations.append(source_info)

        return citations

    async def log_interaction(
        self,
        session_id: str,
        query: str,
        response: str,
        context_mode: ContextMode,
        selected_text: Optional[str],
        sources: List[Dict[str, str]],
        response_time_ms: int,
        accuracy_score: float,
        student_id: Optional[str] = None
    ) -> str:
        """
        Log a chatbot interaction to the database.

        Args:
            session_id: The session identifier
            query: The user's query
            response: The chatbot's response
            context_mode: The context mode used
            selected_text: Text selected by user (if in selected_text mode)
            sources: List of sources used in the response
            response_time_ms: Time taken to generate response
            accuracy_score: Accuracy score of the response
            student_id: Optional student identifier

        Returns:
            ID of the created interaction record
        """
        try:
            interaction = ChatbotInteraction(
                id=str(uuid.uuid4()),
                session_id=session_id,
                student_id=student_id,
                query=query,
                response=response,
                context_mode=context_mode.value,
                selected_text=selected_text,
                timestamp=datetime.utcnow(),
                response_time_ms=response_time_ms,
                accuracy_score=accuracy_score,
                sources=[source["source_document"] for source in sources if "source_document" in source]
            )

            self.db.add(interaction)
            self.db.commit()
            self.db.refresh(interaction)

            logger.info(f"Logged interaction {interaction.id} for session {session_id}")
            return interaction.id

        except Exception as e:
            logger.error(f"Error logging interaction: {e}")
            self.db.rollback()
            raise

    async def update_session_context(
        self,
        session_id: str,
        new_context_mode: Optional[ContextMode] = None,
        new_context_length: Optional[int] = None
    ) -> bool:
        """
        Update session context parameters.

        Args:
            session_id: The session identifier
            new_context_mode: New context mode to set (optional)
            new_context_length: New context length to set (optional)

        Returns:
            True if update was successful, False otherwise
        """
        try:
            session = self.db.query(ChatSession).filter(ChatSession.id == session_id).first()
            if not session:
                logger.warning(f"Session {session_id} not found for context update")
                return False

            if new_context_mode is not None:
                session.context_mode = new_context_mode.value
            if new_context_length is not None:
                session.context_length = new_context_length

            session.last_interaction = datetime.utcnow()
            self.db.commit()

            logger.info(f"Updated context for session {session_id}")
            return True

        except Exception as e:
            logger.error(f"Error updating session context {session_id}: {e}")
            self.db.rollback()
            return False

    async def get_session_stats(
        self,
        session_id: str
    ) -> Dict[str, Any]:
        """
        Get statistics for a specific session.

        Args:
            session_id: The session identifier

        Returns:
            Dictionary with session statistics
        """
        try:
            session = self.db.query(ChatSession).filter(ChatSession.id == session_id).first()
            if not session:
                return {}

            # Get interaction count for this session
            interaction_count = (
                self.db.query(func.count(ChatbotInteraction.id))
                .filter(ChatbotInteraction.session_id == session_id)
                .scalar()
            )

            # Get average response time for this session
            avg_response_time = (
                self.db.query(func.avg(ChatbotInteraction.response_time_ms))
                .filter(ChatbotInteraction.session_id == session_id)
                .scalar()
            )

            # Get average accuracy for this session
            avg_accuracy = (
                self.db.query(func.avg(ChatbotInteraction.accuracy_score))
                .filter(ChatbotInteraction.session_id == session_id)
                .scalar()
            )

            stats = {
                "session_id": session_id,
                "created_at": session.started_at.isoformat(),
                "last_interaction": session.last_interaction.isoformat(),
                "context_mode": session.context_mode,
                "context_length": session.context_length,
                "interaction_count": interaction_count or 0,
                "average_response_time_ms": float(avg_response_time) if avg_response_time else 0,
                "average_accuracy": float(avg_accuracy) if avg_accuracy else 0
            }

            return stats

        except Exception as e:
            logger.error(f"Error getting session stats for {session_id}: {e}")
            return {}

    async def cleanup_expired_sessions(self, hours_old: int = 24) -> int:
        """
        Clean up expired chat sessions (sessions with no activity for specified hours).

        Args:
            hours_old: Sessions older than this many hours will be considered expired

        Returns:
            Number of sessions cleaned up
        """
        try:
            cutoff_time = datetime.utcnow() - timedelta(hours=hours_old)

            expired_sessions = (
                self.db.query(ChatSession)
                .filter(ChatSession.last_interaction < cutoff_time)
                .all()
            )

            count = 0
            for session in expired_sessions:
                # Delete associated interactions first (due to foreign key)
                self.db.query(ChatbotInteraction).filter(
                    ChatbotInteraction.session_id == session.id
                ).delete()

                # Delete the session
                self.db.delete(session)
                count += 1

            self.db.commit()
            logger.info(f"Cleaned up {count} expired sessions older than {hours_old} hours")
            return count

        except Exception as e:
            logger.error(f"Error cleaning up expired sessions: {e}")
            self.db.rollback()
            return 0


# Example usage:
# rag_service = RAGService(
#     similarity_retriever=retriever,
#     embedding_service=embedding_service,
#     db_session=db_session
# )
#
# # Create a new session
# session_id = await rag_service.create_session(
#     student_id="student-uuid",
#     context_mode=ContextMode.GLOBAL
# )
#
# # Process a query
# retrieved_chunks = await retriever.retrieve_by_query("Explain bipedal locomotion")
# response = await llm_service.generate_response(query, retrieved_chunks)
# validation = await rag_service.validate_response(query, response, retrieved_chunks)
#
# if validation.is_valid:
#     # Log the successful interaction
#     await rag_service.log_interaction(
#         session_id=session_id,
#         query=query,
#         response=response,
#         context_mode=ContextMode.GLOBAL,
#         selected_text=None,
#         sources=validation.citations,
#         response_time_ms=500,
#         accuracy_score=validation.confidence_score
#     )