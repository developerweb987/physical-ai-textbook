import asyncio
import logging
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from qdrant_client import QdrantClient
from qdrant_client.http.models import SearchRequest, Filter, FieldCondition, MatchValue, Range
import numpy as np

from .embedding import EmbeddingService

logger = logging.getLogger(__name__)

@dataclass
class RetrievedChunk:
    """Represents a retrieved document chunk with metadata and relevance score."""
    content: str
    source: str
    score: float  # Similarity score between 0 and 1
    metadata: Dict  # Additional metadata about the chunk
    chunk_index: int

class SimilarityRetriever:
    """
    Service for retrieving relevant document chunks based on semantic similarity.
    Uses vector search in Qdrant to find the most relevant content for a query.
    """

    def __init__(
        self,
        qdrant_client: QdrantClient,
        embedding_service: EmbeddingService,
        collection_name: str = "textbook_content",
        top_k: int = 5,
        similarity_threshold: float = 0.3
    ):
        self.qdrant_client = qdrant_client
        self.embedding_service = embedding_service
        self.collection_name = collection_name
        self.top_k = top_k
        self.similarity_threshold = similarity_threshold

    async def retrieve_by_query(
        self,
        query: str,
        chapter_ids: Optional[List[str]] = None,
        top_k: Optional[int] = None
    ) -> List[RetrievedChunk]:
        """
        Retrieve the most relevant document chunks for a query.

        Args:
            query: The query text to search for
            chapter_ids: Optional list of chapter IDs to limit search to specific chapters
            top_k: Optional override for number of results to return

        Returns:
            List of RetrievedChunk objects sorted by relevance score (highest first)
        """
        if top_k is None:
            top_k = self.top_k

        try:
            # Generate embedding for the query
            query_embedding = await self.embedding_service.generate_embedding(query)

            # Prepare filters if chapter IDs are specified
            filters = []
            if chapter_ids:
                # Create a filter for specific chapter IDs
                chapter_filter = FieldCondition(
                    key="metadata.chapter_id",
                    match=MatchValue(any=chapter_ids)
                )
                filters.append(chapter_filter)

            # Create Qdrant search filter
            search_filter = None
            if filters:
                from qdrant_client.http.models import Filter
                search_filter = Filter(must=filters)

            # Perform the search
            search_results = self.qdrant_client.search(
                collection_name=self.collection_name,
                query_vector=query_embedding,
                query_filter=search_filter,
                limit=top_k,
                with_payload=True,
                with_vectors=False
            )

            # Convert results to RetrievedChunk objects
            retrieved_chunks = []
            for hit in search_results:
                # Apply similarity threshold filter
                if hit.score >= self.similarity_threshold:
                    payload = hit.payload
                    chunk = RetrievedChunk(
                        content=payload.get("content", ""),
                        source=payload.get("metadata", {}).get("source", "unknown"),
                        score=hit.score,
                        metadata=payload.get("metadata", {}),
                        chunk_index=payload.get("metadata", {}).get("chunk_index", 0)
                    )
                    retrieved_chunks.append(chunk)

            # Sort by score in descending order
            retrieved_chunks.sort(key=lambda x: x.score, reverse=True)

            logger.debug(f"Retrieved {len(retrieved_chunks)} relevant chunks for query: '{query[:50]}...'")
            return retrieved_chunks

        except Exception as e:
            logger.error(f"Error retrieving documents for query '{query[:50]}...': {e}")
            return []

    async def retrieve_by_selected_text(
        self,
        selected_text: str,
        top_k: Optional[int] = None
    ) -> List[RetrievedChunk]:
        """
        Retrieve contextually related content based on selected text.
        This is used for the "selected text only" mode where we want to find related content
        to the selected text, but not search the entire corpus.

        Args:
            selected_text: The text that was selected by the user
            top_k: Optional override for number of results to return

        Returns:
            List of RetrievedChunk objects related to the selected text
        """
        if top_k is None:
            top_k = self.top_k

        try:
            # Generate embedding for the selected text
            text_embedding = await self.embedding_service.generate_embedding(selected_text)

            # For selected-text mode, we could implement different strategies:
            # 1. Direct search in the vector database
            # 2. Return the selected text itself as context
            # 3. Find closely related content

            # For now, we'll implement a direct search approach
            search_results = self.qdrant_client.search(
                collection_name=self.collection_name,
                query_vector=text_embedding,
                limit=top_k,
                with_payload=True,
                with_vectors=False
            )

            # Convert results to RetrievedChunk objects
            retrieved_chunks = []
            for hit in search_results:
                # Apply similarity threshold filter
                if hit.score >= self.similarity_threshold:
                    payload = hit.payload
                    chunk = RetrievedChunk(
                        content=payload.get("content", ""),
                        source=payload.get("metadata", {}).get("source", "selected_text_context"),
                        score=hit.score,
                        metadata=payload.get("metadata", {}),
                        chunk_index=payload.get("metadata", {}).get("chunk_index", 0)
                    )
                    retrieved_chunks.append(chunk)

            # Sort by score in descending order
            retrieved_chunks.sort(key=lambda x: x.score, reverse=True)

            logger.debug(f"Retrieved {len(retrieved_chunks)} related chunks for selected text: '{selected_text[:50]}...'")
            return retrieved_chunks

        except Exception as e:
            logger.error(f"Error retrieving documents for selected text '{selected_text[:50]}...': {e}")
            return []

    async def retrieve_by_chapter(
        self,
        chapter_id: str,
        query: str,
        top_k: Optional[int] = None
    ) -> List[RetrievedChunk]:
        """
        Retrieve relevant content specifically from a given chapter.

        Args:
            chapter_id: The ID of the chapter to search within
            query: The query text to search for
            top_k: Optional override for number of results to return

        Returns:
            List of RetrievedChunk objects from the specified chapter
        """
        if top_k is None:
            top_k = self.top_k

        try:
            # Generate embedding for the query
            query_embedding = await self.embedding_service.generate_embedding(query)

            # Create filter for specific chapter
            chapter_filter = Filter(
                must=[
                    FieldCondition(
                        key="metadata.chapter_id",
                        match=MatchValue(value=chapter_id)
                    )
                ]
            )

            # Perform the search within the specific chapter
            search_results = self.qdrant_client.search(
                collection_name=self.collection_name,
                query_vector=query_embedding,
                query_filter=chapter_filter,
                limit=top_k,
                with_payload=True,
                with_vectors=False
            )

            # Convert results to RetrievedChunk objects
            retrieved_chunks = []
            for hit in search_results:
                # Apply similarity threshold filter
                if hit.score >= self.similarity_threshold:
                    payload = hit.payload
                    chunk = RetrievedChunk(
                        content=payload.get("content", ""),
                        source=payload.get("metadata", {}).get("source", f"chapter_{chapter_id}"),
                        score=hit.score,
                        metadata=payload.get("metadata", {}),
                        chunk_index=payload.get("metadata", {}).get("chunk_index", 0)
                    )
                    retrieved_chunks.append(chunk)

            # Sort by score in descending order
            retrieved_chunks.sort(key=lambda x: x.score, reverse=True)

            logger.debug(f"Retrieved {len(retrieved_chunks)} relevant chunks from chapter {chapter_id} for query: '{query[:50]}...'")
            return retrieved_chunks

        except Exception as e:
            logger.error(f"Error retrieving documents from chapter {chapter_id} for query '{query[:50]}...': {e}")
            return []

    async def find_related_chunks(
        self,
        chunk_id: str,
        top_k: Optional[int] = None
    ) -> List[RetrievedChunk]:
        """
        Find chunks that are semantically related to a specific chunk.

        Args:
            chunk_id: The ID of the chunk to find related content for
            top_k: Optional override for number of results to return

        Returns:
            List of RetrievedChunk objects related to the specified chunk
        """
        if top_k is None:
            top_k = self.top_k

        try:
            # First, get the original chunk to get its embedding
            original_chunk_result = self.qdrant_client.retrieve(
                collection_name=self.collection_name,
                ids=[chunk_id],
                with_vectors=True
            )

            if not original_chunk_result:
                logger.warning(f"Chunk with ID {chunk_id} not found")
                return []

            original_chunk = original_chunk_result[0]
            original_embedding = original_chunk.vector

            # Search for similar chunks (excluding the original)
            search_results = self.qdrant_client.search(
                collection_name=self.collection_name,
                query_vector=original_embedding,
                limit=top_k + 1,  # Get one extra to exclude the original
                with_payload=True,
                with_vectors=False
            )

            # Convert results to RetrievedChunk objects, excluding the original chunk
            retrieved_chunks = []
            for hit in search_results:
                if hit.id != chunk_id and hit.score >= self.similarity_threshold:  # Exclude original chunk
                    payload = hit.payload
                    chunk = RetrievedChunk(
                        content=payload.get("content", ""),
                        source=payload.get("metadata", {}).get("source", "related_content"),
                        score=hit.score,
                        metadata=payload.get("metadata", {}),
                        chunk_index=payload.get("metadata", {}).get("chunk_index", 0)
                    )
                    retrieved_chunks.append(chunk)

                    # Stop when we have enough results
                    if len(retrieved_chunks) >= top_k:
                        break

            # Sort by score in descending order
            retrieved_chunks.sort(key=lambda x: x.score, reverse=True)

            logger.debug(f"Found {len(retrieved_chunks)} related chunks for chunk {chunk_id}")
            return retrieved_chunks

        except Exception as e:
            logger.error(f"Error finding related chunks for chunk {chunk_id}: {e}")
            return []

    def rerank_results(
        self,
        query: str,
        results: List[RetrievedChunk],
        method: str = "score_only"
    ) -> List[RetrievedChunk]:
        """
        Rerank retrieved results based on additional criteria.

        Args:
            query: The original query
            results: List of retrieved chunks to rerank
            method: Reranking method ('score_only', 'recency_aware', 'diversity_aware')

        Returns:
            Reranked list of RetrievedChunk objects
        """
        if method == "score_only":
            # Already sorted by score, just return
            return results

        elif method == "recency_aware":
            # Boost chunks from more recent chapters/sections
            # This would use metadata about content freshness if available
            scored_results = []
            for chunk in results:
                # Simple recency boost based on chapter number (higher = more recent)
                chapter_num = chunk.metadata.get("chapter_number", 0)
                # Normalize chapter number to 0-1 scale (assuming max 20 chapters)
                recency_boost = min(chapter_num / 20.0, 1.0) if chapter_num > 0 else 0.0
                adjusted_score = chunk.score * 0.7 + recency_boost * 0.3
                scored_results.append((adjusted_score, chunk))

            scored_results.sort(key=lambda x: x[0], reverse=True)
            return [chunk for _, chunk in scored_results]

        elif method == "diversity_aware":
            # Ensure diversity in results (prevent too many chunks from same section)
            # Simple approach: prefer results from different chapters
            seen_chapters = set()
            diverse_results = []

            for chunk in results:
                chapter_id = chunk.metadata.get("chapter_id", "")
                if chapter_id not in seen_chapters:
                    diverse_results.append(chunk)
                    seen_chapters.add(chapter_id)
                    if len(diverse_results) >= len(results) // 2:  # Aim for half diverse
                        break

            # Add remaining results if needed
            for chunk in results:
                if len(diverse_results) >= len(results):
                    break
                if chunk not in diverse_results:
                    diverse_results.append(chunk)

            return diverse_results

        else:
            # Default to score-only ranking
            return results


# Example usage:
# retriever = SimilarityRetriever(
#     qdrant_client=qdrant_client,
#     embedding_service=embedding_service
# )
#
# # Retrieve globally
# results = await retriever.retrieve_by_query("Explain bipedal locomotion in humanoid robots")
#
# # Retrieve from specific chapter
# chapter_results = await retriever.retrieve_by_chapter(
#     chapter_id="some-chapter-id",
#     query="control systems for balance"
# )
#
# # Retrieve in selected-text mode
# selected_results = await retriever.retrieve_by_selected_text(
#     selected_text="Bipedal locomotion requires precise balance control..."
# )