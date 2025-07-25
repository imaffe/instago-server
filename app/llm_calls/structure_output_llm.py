"""
Structure Output LLM for extracting structured data from markdown
"""
import os
from typing import Dict, Literal
from pydantic import BaseModel, Field
import openai

from app.core.logging import get_logger

logger = get_logger(__name__)


# Pydantic models for structured output
class QuickLink(BaseModel):
    type: Literal["direct", "search_str"] = Field(
        description="Type of link: 'direct' for a valid URL, 'search_str' for a search query"
    )
    content: str = Field(
        description="Either a valid URL (when type='direct') or a search string (when type='search_str')"
    )


class StructuredOutput(BaseModel):
    title: str = Field(
        description="A concise, descriptive title for the screenshot content"
    )
    quick_link: QuickLink = Field(
        description="A quick link to access the content - either a direct URL or a search string"
    )


# Prompt for the LLM
STRUCTURE_OUTPUT_PROMPT = """You are an expert at extracting structured information from markdown content about screenshots.

Given the following markdown content about a screenshot, extract:

1. **title**: A concise, descriptive title that captures the main subject of the screenshot
2. **quick_link**: The most relevant link to access or find the content
   - If a direct URL is found in the content, use type="direct" and provide the URL
   - If no direct URL exists but there's enough information to search for it, use type="search_str" and provide a search query

The quick_link should prioritize:
- Original source URLs
- Product pages, article links, or documentation URLs
- GitHub repositories or specific code files
- Social media posts or profiles

If no URL is available, create a search string that would help find:
- The specific product, book, or article
- The author's work or profile
- The specific documentation or code

Markdown content:
{markdown_content}
"""


class StructureOutputLLM:
    """LLM for extracting structured data from markdown using OpenRouter or OpenAI"""

    def __init__(self, provider: str = "openrouter"):
        """
        Initialize the Structure Output LLM

        Args:
            provider: Either "openrouter" or "openai"
        """
        self.provider = provider
        self.initialized = False

        if provider == "openrouter":
            self.api_key = os.getenv("OPENROUTER_API_KEY")
            self.base_url = "https://openrouter.ai/api/v1"
            self.model = "openai/gpt-4o-mini"  # Good for structured output
        else:  # openai
            self.api_key = os.getenv("OPENAI_API_KEY")
            self.base_url = "https://api.openai.com/v1"
            self.model = "gpt-4o-mini"

        if not self.api_key:
            logger.warning(f"No API key found for {provider}")
        else:
            self.client = openai.OpenAI(
                api_key=self.api_key,
                base_url=self.base_url
            )
            self.initialized = True
            logger.info(f"Structure Output LLM initialized with {provider}")

    def extract_structured_data(self, markdown_content: str) -> Dict:
        """
        Extract structured data from markdown content

        Args:
            markdown_content: The markdown string from Claude Agent

        Returns:
            Dictionary with title and quick_link fields
        """
        if not self.initialized:
            logger.error("Structure Output LLM not initialized")
            return self._error_response()

        try:
            # Prepare the prompt
            prompt = STRUCTURE_OUTPUT_PROMPT.format(markdown_content=markdown_content)

            # Make the API call with structured output
            completion = self.client.beta.chat.completions.parse(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert at extracting structured information."},
                    {"role": "user", "content": prompt}
                ],
                response_format=StructuredOutput,
                temperature=0.3,  # Lower temperature for consistent extraction
                max_tokens=500
            )

            # Get the parsed response
            result = completion.choices[0].message.parsed

            # Convert to dictionary
            if result:
                return {
                    "title": result.title,
                    "quick_link": {
                        "type": result.quick_link.type,
                        "content": result.quick_link.content
                    }
                }
            else:
                logger.warning("No parsed result from LLM")
                return self._error_response()

        except Exception as e:
            logger.exception(f"Error extracting structured data: {e}")
            return self._error_response()

    def _error_response(self) -> Dict:
        """Return a default error response"""
        return {
            "title": "Processing Error",
            "quick_link": {
                "type": "search_str",
                "content": "screenshot content"
            }
        }
