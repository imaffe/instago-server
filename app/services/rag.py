"""
RAG (Retrieval-Augmented Generation) service for generating answers from screenshots
"""
from typing import List, Dict, Optional, Tuple, Any, Union
import openai

from app.core.logging import get_logger
from app.core.config import settings

logger = get_logger(__name__)


class RAGService:
    """Service for generating answers using retrieved screenshots as context"""
    
    def __init__(self, provider: str = "openai"):
        """
        Initialize the RAG service
        
        Args:
            provider: Model provider - "openai", "openrouter", or "moonshot"
        """
        self.provider = provider
        self.initialized = False
        
        if provider == "openai":
            self.api_key = settings.OPENAI_API_KEY
            self.model = settings.OPENAI_MODEL  # gpt-4o
            self.client = openai.OpenAI(api_key=self.api_key)
        elif provider == "openrouter":
            self.api_key = settings.OPENROUTER_API_KEY
            self.model = "openai/gpt-4o"
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
            logger.info(f"RAG service initialized with {provider}")
        else:
            logger.warning(f"No API key found for {provider}")
    
    def generate_answer(
        self,
        query: str,
        screenshots: List[Tuple[Union[Dict, object], float]],
        max_context_screenshots: int = 5
    ) -> Dict[str, Any]:
        """
        Generate an answer based on the query and retrieved screenshots
        
        Args:
            query: User's search query
            screenshots: List of tuples (screenshot_data, relevance_score) sorted by relevance
            max_context_screenshots: Maximum number of screenshots to use as context
            
        Returns:
            Dictionary with generated answer and metadata
        """
        if not self.initialized:
            logger.warning("RAG service not initialized")
            return {
                "answer": "Unable to generate answer - RAG service not initialized",
                "sources_used": 0,
                "confidence": 0.0
            }
        
        try:
            # Select top screenshots for context
            context_screenshots = screenshots[:max_context_screenshots]
            
            # Build the context from screenshots
            context = self._build_context(context_screenshots)
            
            # Generate the answer
            prompt = self._build_rag_prompt(query, context)
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self._get_system_prompt()},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7 if self.provider == "moonshot" else 0.5,
                max_tokens=1000
            )
            
            answer = response.choices[0].message.content or "No answer generated"
            
            # Calculate confidence based on relevance scores
            avg_relevance = sum(score for _, score in context_screenshots) / len(context_screenshots) if context_screenshots else 0
            
            return {
                "answer": answer,
                "sources_used": len(context_screenshots),
                "confidence": avg_relevance,
                "model_used": f"{self.provider}/{self.model}"
            }
            
        except Exception as e:
            logger.error(f"Error generating answer: {e}")
            return {
                "answer": f"Error generating answer: {str(e)}",
                "sources_used": 0,
                "confidence": 0.0
            }
    
    def _get_system_prompt(self) -> str:
        """Get the system prompt for RAG"""
        return """You are a helpful assistant that answers questions based on screenshot content.
Your task is to provide accurate, relevant answers using ONLY the information from the provided screenshots.

Guidelines:
1. Base your answer strictly on the screenshot content provided
2. If the screenshots don't contain enough information, say so clearly
3. Reference specific screenshots when possible (e.g., "According to Screenshot 1...")
4. Be concise but comprehensive
5. If multiple screenshots contain relevant information, synthesize it coherently
6. Maintain the original language of the query in your response

Important: Do not make up information. Only use what's in the screenshots."""
    
    def _build_context(self, screenshots: List[Tuple[Union[Dict, object], float]]) -> str:
        """Build context string from screenshots"""
        context = ""
        
        for i, (screenshot, score) in enumerate(screenshots):
            context += f"\n--- Screenshot {i+1} (Relevance: {score:.2f}) ---\n"
            
            # Handle both dict and object types
            if isinstance(screenshot, dict):
                title = screenshot.get('ai_title', 'No title')
                description = screenshot.get('ai_description', 'No description')
                markdown = screenshot.get('markdown_content', '')
                tags = screenshot.get('ai_tags', [])
            else:
                # Assume it's a ScreenshotDTO object
                title = getattr(screenshot, 'ai_title', 'No title')
                description = getattr(screenshot, 'ai_description', 'No description')
                markdown = getattr(screenshot, 'markdown_content', '')
                tags = getattr(screenshot, 'ai_tags', [])
            
            context += f"Title: {title}\n"
            context += f"Description: {description}\n"
            
            # Include markdown content
            if markdown:
                # Limit markdown length to prevent context overflow
                max_length = 1000
                if len(markdown) > max_length:
                    markdown = markdown[:max_length] + "\n[Content truncated...]"
                context += f"Content:\n{markdown}\n"
            
            # Include tags if available
            if tags:
                context += f"Tags: {', '.join(tags)}\n"
            
            context += "\n"
        
        return context
    
    def _build_rag_prompt(self, query: str, context: str) -> str:
        """Build the RAG prompt"""
        return f"""Based on the following screenshots, please answer this query:

Query: {query}

Screenshot Context:
{context}

Please provide a comprehensive answer based ONLY on the information in the screenshots above. If the screenshots don't contain enough information to fully answer the query, clearly state what information is missing."""


# Create singleton instance with OpenAI as default
rag_service = RAGService()