import asyncio
import logging
from typing import List, Union
import numpy as np
import openai
from openai import AsyncOpenAI
import tiktoken

logger = logging.getLogger(__name__)

class EmbeddingService:
    """
    Service for generating embeddings for text content used in RAG.
    Uses OpenAI's embedding API for consistent, high-quality embeddings.
    """

    def __init__(self, openai_api_key: str, model_name: str = "text-embedding-3-small"):
        self.client = AsyncOpenAI(api_key=openai_api_key)
        self.model_name = model_name
        self.tokenizer = tiktoken.encoding_for_model("text-embedding-3-small")  # Closest match for token counting

    async def generate_embedding(self, text: str) -> List[float]:
        """
        Generate a single embedding for the provided text.

        Args:
            text: The text to generate an embedding for

        Returns:
            A list of floats representing the embedding vector
        """
        try:
            # Truncate text if it's too long (OpenAI has token limits)
            tokens = self.tokenizer.encode(text)
            if len(tokens) > 8191:  # OpenAI's max for text-embedding-3-small is 8191 tokens
                logger.warning(f"Text too long ({len(tokens)} tokens), truncating to 8191 tokens")
                tokens = tokens[:8191]
                text = self.tokenizer.decode(tokens)

            response = await self.client.embeddings.create(
                input=text,
                model=self.model_name
            )

            embedding = response.data[0].embedding
            logger.debug(f"Generated embedding of length {len(embedding)} for text of length {len(text)}")
            return embedding

        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            raise

    async def generate_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts in a batch.

        Args:
            texts: List of texts to generate embeddings for

        Returns:
            A list of embedding vectors (each a list of floats)
        """
        try:
            # Truncate long texts to avoid token limit issues
            processed_texts = []
            for text in texts:
                tokens = self.tokenizer.encode(text)
                if len(tokens) > 8191:
                    logger.warning(f"Text too long ({len(tokens)} tokens), truncating to 8191 tokens")
                    tokens = tokens[:8191]
                    text = self.tokenizer.decode(tokens)
                processed_texts.append(text)

            response = await self.client.embeddings.create(
                input=processed_texts,
                model=self.model_name
            )

            embeddings = [item.embedding for item in response.data]
            logger.debug(f"Generated {len(embeddings)} embeddings in batch")
            return embeddings

        except Exception as e:
            logger.error(f"Error generating batch embeddings: {e}")
            raise

    def calculate_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """
        Calculate cosine similarity between two embedding vectors.

        Args:
            vec1: First embedding vector
            vec2: Second embedding vector

        Returns:
            Cosine similarity score between 0 and 1
        """
        # Convert to numpy arrays
        arr1 = np.array(vec1)
        arr2 = np.array(vec2)

        # Calculate cosine similarity
        dot_product = np.dot(arr1, arr2)
        norm1 = np.linalg.norm(arr1)
        norm2 = np.linalg.norm(arr2)

        if norm1 == 0 or norm2 == 0:
            return 0.0

        similarity = dot_product / (norm1 * norm2)
        # Ensure similarity is between 0 and 1
        return max(0.0, min(1.0, float(similarity)))

    def normalize_vector(self, vector: List[float]) -> List[float]:
        """
        Normalize an embedding vector to unit length.

        Args:
            vector: The embedding vector to normalize

        Returns:
            Normalized embedding vector
        """
        arr = np.array(vector)
        norm = np.linalg.norm(arr)
        if norm == 0:
            return vector  # Return original if zero vector
        normalized_arr = arr / norm
        return normalized_arr.tolist()

    async def get_text_token_count(self, text: str) -> int:
        """
        Get the number of tokens in a text using the appropriate tokenizer.

        Args:
            text: The text to count tokens for

        Returns:
            Number of tokens in the text
        """
        tokens = self.tokenizer.encode(text)
        return len(tokens)

    def chunk_text_by_tokens(self, text: str, max_tokens: int = 512, overlap_tokens: int = 50) -> List[str]:
        """
        Split text into chunks based on token count rather than character count.

        Args:
            text: The text to chunk
            max_tokens: Maximum number of tokens per chunk
            overlap_tokens: Number of tokens to overlap between chunks

        Returns:
            List of text chunks
        """
        tokens = self.tokenizer.encode(text)

        chunks = []
        start_idx = 0

        while start_idx < len(tokens):
            end_idx = start_idx + max_tokens

            # If we're at the end, just take the remaining tokens
            if end_idx >= len(tokens):
                chunk_tokens = tokens[start_idx:]
                chunk_text = self.tokenizer.decode(chunk_tokens)
                if chunk_text.strip():  # Only add non-empty chunks
                    chunks.append(chunk_text)
                break

            # Get the chunk
            chunk_tokens = tokens[start_idx:end_idx]
            chunk_text = self.tokenizer.decode(chunk_tokens)

            # Add the chunk
            if chunk_text.strip():  # Only add non-empty chunks
                chunks.append(chunk_text)

            # Move to the next chunk with overlap
            start_idx = end_idx - overlap_tokens

        return chunks


# Example usage:
# embedding_service = EmbeddingService(openai_api_key=os.getenv("OPENAI_API_KEY"))
#
# # Generate single embedding
# embedding = await embedding_service.generate_embedding("This is a sample text")
#
# # Generate batch embeddings
# texts = ["Text 1", "Text 2", "Text 3"]
# embeddings = await embedding_service.generate_embeddings_batch(texts)
#
# # Calculate similarity between two embeddings
# similarity = embedding_service.calculate_similarity(embedding1, embedding2)