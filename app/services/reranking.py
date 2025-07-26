"""
Reranking service for improving search results using cross-encoder models
"""
from typing import List, Dict, Tuple, Union
import openai

from app.core.logging import get_logger
from app.core.config import settings

logger = get_logger(__name__)


class RerankingService:
    """Service for reranking search results using cross-encoder approach"""

    def __init__(self, provider: str = "openai"):
        """
        Initialize the reranking service

        Args:
            provider: Model provider - "openai", "openrouter", or "moonshot"
        """
        self.provider = provider
        self.initialized = False

        if provider == "openai":
            self.api_key = settings.OPENAI_API_KEY
            self.model = "gpt-4o-mini"
            self.client = openai.OpenAI(api_key=self.api_key)
        elif provider == "openrouter":
            self.api_key = settings.OPENROUTER_API_KEY
            self.model = "openai/gpt-4o-mini"
            self.client = openai.OpenAI(
                api_key=self.api_key,
                base_url="https://openrouter.ai/api/v1"
            )
        elif provider == "moonshot":
            self.api_key = settings.MOONSHOT_API_KEY
            self.model = settings.MOONSHOT_MODEL
            self.client = openai.OpenAI(
                api_key=self.api_key,
                base_url=settings.MOONSHOT_BASE_URL
            )

        if self.api_key:
            self.initialized = True
            logger.info(f"Reranking service initialized with {provider}")
        else:
            logger.warning(f"No API key found for {provider}")

    def rerank_screenshots(
        self,
        query: str,
        screenshots: List[Union[Dict, object]],
        top_k: int = 3
    ) -> List[Tuple[Union[Dict, object], float]]:
        """
        Rerank screenshots based on relevance to query

        Args:
            query: User's search query
            screenshots: List of screenshot data with ai_title, ai_description, markdown_content
            top_k: Number of top results to return

        Returns:
            List of tuples (screenshot, relevance_score) sorted by relevance
        """
        if not self.initialized:
            logger.warning("Reranking service not initialized, returning original order")
            return [(s, 1.0) for s in screenshots[:top_k]]

        try:
            # Prepare the reranking prompt
            rerank_prompt = self._build_reranking_prompt(query, screenshots)

            # Call the model for reranking
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self._get_system_prompt()},
                    {"role": "user", "content": rerank_prompt}
                ],
                temperature=0.3,
                max_tokens=1000
            )

            # Parse the response to get rankings
            content = response.choices[0].message.content
            if not content:
                logger.warning("No content in reranking response")
                return [(s, 1.0) for s in screenshots[:top_k]]

            rankings = self._parse_rankings(content)

            # Sort screenshots by ranking
            reranked = []
            for idx, score in rankings[:top_k]:
                if idx < len(screenshots):
                    reranked.append((screenshots[idx], score))

            # Add any missing screenshots with low scores
            included_indices = {idx for idx, _ in rankings[:top_k]}
            for i, screenshot in enumerate(screenshots):
                if i not in included_indices and len(reranked) < top_k:
                    reranked.append((screenshot, 0.5))

            logger.info(f"Reranked {len(screenshots)} results, returning top {len(reranked)}")
            return reranked[:top_k]

        except Exception as e:
            logger.error(f"Error in reranking: {e}")
            # Fallback to original order
            return [(s, 1.0) for s in screenshots[:top_k]]

    def _get_system_prompt(self) -> str:
        """Get the system prompt for reranking"""
        return """You are an expert at evaluating the relevance of screenshots to search queries.
Your task is to analyze screenshots and rank them by relevance to the user's query.

Consider:
1. Semantic similarity between query and screenshot content
2. Whether the screenshot directly answers or relates to the query
3. The quality and completeness of information in the screenshot
4. User intent behind the query

Output format: List each screenshot index with its relevance score (0-1).
Example:
0: 0.95
2: 0.87
1: 0.65
3: 0.45
..."""

    def _build_reranking_prompt(self, query: str, screenshots: List[Union[Dict, object]]) -> str:
        """Build the prompt for reranking screenshots"""
        prompt = f"Query: {query}\n\n"
        prompt += "Screenshots to rank:\n\n"

        for i, screenshot in enumerate(screenshots):
            prompt += f"Screenshot {i}:\n"

            # Handle both dict and object types
            if isinstance(screenshot, dict):
                title = screenshot.get('ai_title', 'No title')
                description = screenshot.get('ai_description', 'No description')
                markdown = screenshot.get('markdown_content', '')
            else:
                # Assume it's a ScreenshotDTO object
                title = getattr(screenshot, 'ai_title', 'No title')
                description = getattr(screenshot, 'ai_description', 'No description')
                markdown = getattr(screenshot, 'markdown_content', '')

            prompt += f"Title: {title}\n"
            prompt += f"Description: {description}\n"

            # Include a snippet of markdown content
            if markdown:
                # Take first 300 characters of markdown
                snippet = markdown[:300] + "..." if len(markdown) > 300 else markdown
                prompt += f"Content snippet: {snippet}\n"

            prompt += "\n"

        prompt += "\nRank these screenshots by relevance to the query. List them in order with relevance scores."
        return prompt

    def _parse_rankings(self, response: str) -> List[Tuple[int, float]]:
        """Parse the ranking response to extract indices and scores"""
        rankings = []

        lines = response.strip().split('\n')
        for line in lines:
            if ':' in line:
                try:
                    parts = line.split(':')
                    idx = int(parts[0].strip())
                    score = float(parts[1].strip())
                    rankings.append((idx, score))
                except (ValueError, IndexError):
                    continue

        # Sort by score descending
        rankings.sort(key=lambda x: x[1], reverse=True)
        return rankings


# Create singleton instance
reranking_service = RerankingService()
