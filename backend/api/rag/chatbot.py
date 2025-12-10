import asyncio
import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass
from enum import Enum
import openai
import numpy as np
from qdrant_client import QdrantClient
from qdrant_client.http.models import PointStruct, VectorParams, Distance, Filter, FieldCondition, MatchValue

from ..models.content import ChatbotInteraction, ChatSession, DocumentChunk
from ..database import SessionLocal

logger = logging.getLogger(__name__)

class ContextMode(str, Enum):
    GLOBAL = "global"
    SELECTED_TEXT = "selected_text"

@dataclass
class ChatResponse:
    response: str
    sources: List[Dict]
    confidence: float
    session_id: Optional[str] = None

class RAGChatbotService:
    """
    Service for handling RAG (Retrieval-Augmented Generation) chatbot functionality
    with support for both global (entire book) and selected-text-only modes.
    """

    def __init__(self, openai_api_key: str, qdrant_url: str, qdrant_api_key: str, model_name: str = "gpt-3.5-turbo"):
        self.openai_client = openai.OpenAI(api_key=openai_api_key)
        self.qdrant_client = QdrantClient(url=qdrant_url, api_key=qdrant_api_key)
        self.model_name = model_name
        self.collection_name = "textbook_content"

        # Initialize Qdrant collection if it doesn't exist
        self._initialize_collection()

    def _initialize_collection(self):
        """Initialize the Qdrant collection for storing document embeddings."""
        try:
            collections = self.qdrant_client.get_collections()
            if self.collection_name not in [col.name for col in collections.collections]:
                self.qdrant_client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(size=1536, distance=Distance.COSINE)  # Assuming OpenAI ada embedding size
                )
                logger.info(f"Created Qdrant collection: {self.collection_name}")
            else:
                logger.info(f"Qdrant collection {self.collection_name} already exists")
        except Exception as e:
            logger.error(f"Error initializing Qdrant collection: {e}")
            raise

    async def query(
        self,
        query: str,
        context_mode: ContextMode,
        session_id: Optional[str] = None,
        selected_text: Optional[str] = None,
        student_id: Optional[str] = None
    ) -> ChatResponse:
        """
        Process a query using RAG with either global or selected-text context mode.

        Args:
            query: The question from the user
            context_mode: Whether to use global or selected-text context
            session_id: Optional session identifier for conversation context
            selected_text: Text selected by user (required if context_mode is SELECTED_TEXT)
            student_id: Optional student identifier

        Returns:
            ChatResponse with the answer, sources, and confidence score
        """
        start_time = datetime.utcnow()

        try:
            # Retrieve relevant documents based on context mode
            if context_mode == ContextMode.SELECTED_TEXT:
                if not selected_text:
                    raise ValueError("selected_text is required when context_mode is SELECTED_TEXT")

                # For selected-text mode, we'll use the provided text directly
                relevant_docs = [{"content": selected_text, "source": "selected_text", "score": 1.0}]
            else:  # GLOBAL mode
                relevant_docs = await self._retrieve_relevant_documents(query)

            # Generate response using the retrieved context
            response, sources, confidence = await self._generate_response(query, relevant_docs)

            # Calculate response time
            response_time = (datetime.utcnow() - start_time).total_seconds() * 1000  # ms

            # Log the interaction
            await self._log_interaction(
                query=query,
                response=response,
                context_mode=context_mode.value,
                selected_text=selected_text,
                sources=sources,
                response_time_ms=int(response_time),
                accuracy_score=confidence,
                student_id=student_id
            )

            return ChatResponse(
                response=response,
                sources=sources,
                confidence=confidence,
                session_id=session_id
            )
        except Exception as e:
            logger.error(f"Error processing chat query: {e}")
            # Implement fallback mechanism
            fallback_response = await self._fallback_query(query)
            return ChatResponse(
                response=fallback_response,
                sources=[{"source": "fallback", "content": "Fallback response due to system issue"}],
                confidence=0.5
            )

    async def _retrieve_relevant_documents(self, query: str, top_k: int = 5) -> List[Dict]:
        """Retrieve the most relevant document chunks for the query."""
        try:
            # Generate embedding for the query
            query_embedding = await self._generate_embedding(query)

            # Search in Qdrant
            search_result = self.qdrant_client.search(
                collection_name=self.collection_name,
                query_vector=query_embedding,
                limit=top_k
            )

            # Format results
            relevant_docs = []
            for hit in search_result:
                relevant_docs.append({
                    "content": hit.payload.get("content", ""),
                    "source": hit.payload.get("source", ""),
                    "score": hit.score,
                    "metadata": hit.payload.get("metadata", {})
                })

            return relevant_docs
        except Exception as e:
            logger.error(f"Error retrieving documents: {e}")
            return []

    async def _generate_response(self, query: str, relevant_docs: List[Dict]) -> Tuple[str, List[Dict], float]:
        """Generate a response using the query and relevant documents."""
        # Create context from relevant documents
        context = "\n\n".join([doc["content"] for doc in relevant_docs])

        # Create a more detailed prompt for better responses
        system_prompt = (
            "You are an AI assistant for a Physical AI & Humanoid Robotics textbook. "
            "Provide accurate, educational responses based on the provided textbook content. "
            "Cite sources when possible and maintain academic rigor. "
            "If the information is not in the provided context, say so explicitly."
        )

        user_prompt = (
            f"Context:\n{context}\n\n"
            f"Question: {query}\n\n"
            "Please provide a comprehensive answer based on the context, citing sources when possible."
        )

        try:
            response = self.openai_client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3,  # Lower temperature for more consistent, factual responses
                max_tokens=1000
            )

            answer = response.choices[0].message.content
            # For now, confidence is based on the number of sources and their relevance scores
            avg_score = sum(doc.get("score", 0) for doc in relevant_docs) / max(len(relevant_docs), 1)
            confidence = min(avg_score, 1.0)  # Clamp to 0-1 range

            # Format sources
            sources = []
            for doc in relevant_docs:
                sources.append({
                    "content_snippet": doc["content"][:200] + "..." if len(doc["content"]) > 200 else doc["content"],
                    "source": doc["source"],
                    "relevance_score": doc.get("score", 0.0)
                })

            return answer, sources, confidence

        except Exception as e:
            logger.error(f"Error generating response: {e}")
            raise

    async def _generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for text using OpenAI API."""
        try:
            response = self.openai_client.embeddings.create(
                input=text,
                model="text-embedding-3-small"  # Using smaller, more efficient model
            )
            return response.data[0].embedding
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            raise

    async def _log_interaction(
        self,
        query: str,
        response: str,
        context_mode: str,
        selected_text: Optional[str],
        sources: List[Dict],
        response_time_ms: int,
        accuracy_score: float,
        student_id: Optional[str]
    ):
        """Log the chat interaction to the database."""
        db = SessionLocal()
        try:
            interaction = ChatbotInteraction(
                query=query,
                response=response,
                context_mode=context_mode,
                selected_text=selected_text,
                response_time_ms=response_time_ms,
                accuracy_score=accuracy_score,
                sources=[source["source"] for source in sources],
                student_id=student_id
            )
            db.add(interaction)
            db.commit()
            db.refresh(interaction)
        except Exception as e:
            logger.error(f"Error logging interaction: {e}")
        finally:
            db.close()

    async def _fallback_query(self, query: str) -> str:
        """Fallback query mechanism if primary service fails."""
        logger.warning("Using fallback query mechanism")
        return f"I received your query: '{query}'. Due to a temporary issue with the AI service, I cannot provide a detailed answer right now. Please try again later or consult the relevant textbook chapters directly."

    async def create_session(self, student_id: Optional[str] = None, context_mode: ContextMode = ContextMode.GLOBAL) -> str:
        """Create a new chat session."""
        db = SessionLocal()
        try:
            session = ChatSession(
                student_id=student_id,
                context_mode=context_mode.value
            )
            db.add(session)
            db.commit()
            db.refresh(session)
            return str(session.id)
        except Exception as e:
            logger.error(f"Error creating session: {e}")
            raise
        finally:
            db.close()


# Example usage:
# chatbot_service = RAGChatbotService(
#     openai_api_key=os.getenv("OPENAI_API_KEY"),
#     qdrant_url=os.getenv("QDRANT_URL"),
#     qdrant_api_key=os.getenv("QDRANT_API_KEY")
# )
#
# response = await chatbot_service.query(
#     query="Explain the principles of bipedal locomotion in humanoid robots",
#     context_mode=ContextMode.GLOBAL
# )
# print(response.response)
# print(f"Confidence: {response.confidence}")
# print(f"Sources: {response.sources}")