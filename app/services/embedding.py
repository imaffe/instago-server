from typing import List

from openai import OpenAI

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class EmbeddingService:
    """Dedicated service for generating text embeddings"""

    def __init__(self):
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = "text-embedding-3-small"  # OpenAI's latest small embedding model
        self.dimension = settings.OPENAI_EMBEDDING_DIM

    def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for a text string

        Args:
            text: Text to generate embedding for

        Returns:
            List of floats representing the embedding vector
        """
        try:
            if not text or not text.strip():
                logger.warning("Empty text provided for embedding generation")
                return [0.0] * self.dimension

            response = self.client.embeddings.create(
                model=self.model,
                input=text
            )

            embedding = response.data[0].embedding
            logger.debug(f"Generated embedding of dimension {len(embedding)} for text of length {len(text)}")

            return embedding

        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            logger.exception("Full stack trace:")
            return [0.0] * self.dimension

    def generate_embedding_from_screenshot_data(
        self,
        title: str,
        description: str,
        tags: List[str],
        markdown: str
    ) -> List[float]:
        """
        Generate embedding from screenshot AI analysis results

        Args:
            title: AI-generated title
            description: AI-generated description
            tags: List of AI-generated tags
            markdown: AI-generated markdown content

        Returns:
            List of floats representing the embedding vector
        """
        # Combine all text data for comprehensive embedding
        combined_text = f"{title}\n\n{description}\n\n{' '.join(tags)}\n\n{markdown}"

        return self.generate_embedding(combined_text)


# Singleton instance
embedding_service = EmbeddingService()
