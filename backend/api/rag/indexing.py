import asyncio
import logging
from typing import List, Dict, Any
from uuid import UUID
import hashlib
from sqlalchemy.orm import Session
from qdrant_client import QdrantClient
from qdrant_client.http.models import PointStruct, Batch

from ..models.content import TextbookChapter, DocumentChunk
from ..database import SessionLocal
from .embedding import generate_embedding

logger = logging.getLogger(__name__)

class ContentIndexer:
    """
    Service for indexing textbook content for RAG functionality.
    Handles chunking, embedding, and storing content in vector database.
    """

    def __init__(self, qdrant_client: QdrantClient, collection_name: str = "textbook_content"):
        self.qdrant_client = qdrant_client
        self.collection_name = collection_name

    def chunk_text(self, text: str, chunk_size: int = 512, overlap: int = 50) -> List[Dict[str, Any]]:
        """
        Split text into overlapping chunks while preserving semantic boundaries.

        Args:
            text: The text to chunk
            chunk_size: Maximum size of each chunk in tokens (approximate)
            overlap: Number of tokens to overlap between chunks

        Returns:
            List of dictionaries containing chunk content and metadata
        """
        # For simplicity, we'll use character-based chunking
        # In a real implementation, this would use tokenizers
        sentences = self._split_into_sentences(text)

        chunks = []
        current_chunk = ""
        current_pos = 0

        for sentence in sentences:
            # Check if adding this sentence would exceed chunk size
            if len(current_chunk) + len(sentence) > chunk_size and current_chunk:
                # Save the current chunk
                chunks.append({
                    "content": current_chunk.strip(),
                    "start_pos": current_pos,
                    "end_pos": current_pos + len(current_chunk)
                })

                # Start new chunk with overlap
                if overlap > 0:
                    # Find overlap from the end of current chunk
                    overlap_start = max(0, len(current_chunk) - overlap)
                    current_chunk = current_chunk[overlap_start:] + " " + sentence
                else:
                    current_chunk = sentence

                current_pos = current_pos + len(current_chunk) - len(sentence)
            else:
                current_chunk += " " + sentence if current_chunk else sentence

        # Add the last chunk if it has content
        if current_chunk.strip():
            chunks.append({
                "content": current_chunk.strip(),
                "start_pos": current_pos,
                "end_pos": current_pos + len(current_chunk)
            })

        return chunks

    def _split_into_sentences(self, text: str) -> List[str]:
        """Split text into sentences while preserving context."""
        import re
        # Simple sentence splitting - in practice, would use a proper NLP library
        sentences = re.split(r'[.!?]+\s+', text)
        # Re-add punctuation
        sentences = [s + '.' if not s.endswith(('.', '!', '?')) and s.strip() else s for s in sentences]
        return [s for s in sentences if s.strip()]

    async def index_chapter(self, chapter_id: UUID) -> bool:
        """
        Index a specific textbook chapter by creating document chunks and storing embeddings.

        Args:
            chapter_id: The ID of the chapter to index

        Returns:
            True if indexing was successful, False otherwise
        """
        db = SessionLocal()
        try:
            # Get the chapter from the database
            chapter = db.query(TextbookChapter).filter(TextbookChapter.id == chapter_id).first()
            if not chapter:
                logger.error(f"Chapter with ID {chapter_id} not found")
                return False

            # Create chunks from the chapter content
            chunks = self.chunk_text(chapter.content)

            # Process each chunk
            points = []
            for i, chunk_data in enumerate(chunks):
                # Generate embedding for the chunk
                embedding = await generate_embedding(chunk_data["content"])

                # Create a unique ID for this chunk
                chunk_id = str(hashlib.md5(f"{chapter_id}_{i}".encode()).hexdigest())

                # Create metadata for the chunk
                metadata = {
                    "chapter_id": str(chapter.id),
                    "chapter_title": chapter.title,
                    "chapter_number": chapter.chapter_number,
                    "chunk_index": i,
                    "start_pos": chunk_data["start_pos"],
                    "end_pos": chunk_data["end_pos"],
                    "source": f"chapter_{chapter.slug}_chunk_{i}"
                }

                # Create a Qdrant point
                point = PointStruct(
                    id=chunk_id,
                    vector=embedding,
                    payload={
                        "content": chunk_data["content"],
                        "metadata": metadata
                    }
                )
                points.append(point)

                # Also save to our database for reference
                document_chunk = DocumentChunk(
                    id=UUID(chunk_id),
                    chapter_id=chapter.id,
                    content=chunk_data["content"],
                    chunk_index=i,
                    metadata=metadata
                )
                db.add(document_chunk)

            # Upload all points to Qdrant in a batch
            if points:
                self.qdrant_client.upsert(
                    collection_name=self.collection_name,
                    points=Batch(
                        ids=[p.id for p in points],
                        vectors=[p.vector for p in points],
                        payloads=[p.payload for p in points]
                    )
                )

                # Commit database changes
                db.commit()

                logger.info(f"Successfully indexed chapter {chapter_id} with {len(points)} chunks")
                return True
            else:
                logger.warning(f"No chunks created for chapter {chapter_id}")
                return True  # Still successful, just no content to index

        except Exception as e:
            logger.error(f"Error indexing chapter {chapter_id}: {e}")
            db.rollback()
            return False
        finally:
            db.close()

    async def index_all_chapters(self) -> bool:
        """
        Index all published textbook chapters.

        Returns:
            True if all chapters were indexed successfully, False otherwise
        """
        db = SessionLocal()
        try:
            # Get all published chapters
            chapters = db.query(TextbookChapter).filter(TextbookChapter.status == 'published').all()

            success_count = 0
            for chapter in chapters:
                success = await self.index_chapter(chapter.id)
                if success:
                    success_count += 1
                else:
                    logger.error(f"Failed to index chapter {chapter.id}")

            logger.info(f"Indexed {success_count}/{len(chapters)} chapters successfully")
            return success_count == len(chapters)

        except Exception as e:
            logger.error(f"Error indexing all chapters: {e}")
            return False
        finally:
            db.close()

    async def delete_chapter_index(self, chapter_id: UUID) -> bool:
        """
        Remove all chunks for a specific chapter from the index.

        Args:
            chapter_id: The ID of the chapter to remove from index

        Returns:
            True if deletion was successful, False otherwise
        """
        try:
            # Get all chunk IDs for this chapter from our database
            db = SessionLocal()
            try:
                chunk_ids = db.query(DocumentChunk.id).filter(DocumentChunk.chapter_id == chapter_id).all()
                chunk_ids = [str(chunk_id[0]) for chunk_id in chunk_ids]

                if chunk_ids:
                    # Delete from Qdrant
                    self.qdrant_client.delete(
                        collection_name=self.collection_name,
                        points_selector=chunk_ids
                    )

                    # Delete from our database
                    db.query(DocumentChunk).filter(DocumentChunk.chapter_id == chapter_id).delete()
                    db.commit()

                    logger.info(f"Deleted {len(chunk_ids)} chunks for chapter {chapter_id}")

                return True
            finally:
                db.close()

        except Exception as e:
            logger.error(f"Error deleting chapter index for {chapter_id}: {e}")
            return False

    async def update_chapter_index(self, chapter_id: UUID) -> bool:
        """
        Update the index for a specific chapter by removing old chunks and adding new ones.

        Args:
            chapter_id: The ID of the chapter to update

        Returns:
            True if update was successful, False otherwise
        """
        try:
            # First delete the old index
            await self.delete_chapter_index(chapter_id)

            # Then create the new index
            success = await self.index_chapter(chapter_id)

            if success:
                logger.info(f"Successfully updated index for chapter {chapter_id}")
            else:
                logger.error(f"Failed to update index for chapter {chapter_id}")

            return success

        except Exception as e:
            logger.error(f"Error updating chapter index for {chapter_id}: {e}")
            return False


# Example usage:
# indexer = ContentIndexer(qdrant_client=qdrant_client)
#
# # Index a specific chapter
# await indexer.index_chapter(UUID("some-chapter-id"))
#
# # Index all published chapters
# await indexer.index_all_chapters()
#
# # Update index when chapter content changes
# await indexer.update_chapter_index(UUID("some-chapter-id"))