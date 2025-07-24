import json
from typing import Dict, List

import vertexai
from vertexai.generative_models import GenerativeModel, Part, GenerationConfig

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class GeminiAgent:
    def __init__(self):
        self.initialized = False
        if settings.VERTEX_AI_PROJECT:
            try:
                # Initialize Vertex AI
                vertexai.init(
                    project=settings.VERTEX_AI_PROJECT,
                    location=settings.VERTEX_AI_LOCATION
                )
                self.model = GenerativeModel(settings.GEMINI_MODEL)
                self.initialized = True
                logger.info("Gemini agent initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Gemini agent: {e}")
                self.initialized = False

    def process_screenshot(self, image_bytes: bytes) -> Dict:
        if not self.initialized:
            logger.error("Gemini agent not initialized")
            return self._error_response()

        try:
            # Create image part for Vertex AI
            image_part = Part.from_data(
                data=image_bytes,
                mime_type="image/png"
            )

            prompt = """Analyze this screenshot and provide comprehensive metadata.

            You must return a JSON object with the following structure:
            {
                "title": "A concise, descriptive title (max 200 chars)",
                "description": "A detailed description of what's shown",
                "tags": ["relevant", "tags", "for", "categorization"],
                "markdown": "A rich markdown document with:\n- Summary of the content\n- Key information extracted\n- Relevant links and resources (if identifiable)\n- Actionable insights"
            }

            Focus on:
            1. Identifying the application or website shown
            2. Extracting text content and key information
            3. Understanding the context and purpose
            4. Providing useful tags for search and organization
            5. Creating helpful markdown documentation
            """

            generation_config = GenerationConfig(
                temperature=0.3,
                max_output_tokens=2048,
                response_mime_type="application/json"
            )

            response = self.model.generate_content(
                [prompt, image_part],
                generation_config=generation_config
            )

            # Parse the JSON response
            result = json.loads(response.text)

            return {
                "title": result.get("title", "Untitled Screenshot"),
                "description": result.get("description", ""),
                "tags": result.get("tags", []),
                "markdown": result.get("markdown", "")
            }

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Gemini response as JSON: {e}")
            return self._error_response()
        except Exception as e:
            logger.error(f"Error processing screenshot with Gemini: {e}")
            return self._error_response()

    def generate_embedding(self, text: str) -> List[float]:
        # Note: Gemini doesn't directly provide embeddings like OpenAI
        # You would need to use a different model or service for embeddings
        # For now, we'll return None to indicate embeddings should be handled elsewhere
        logger.info("Gemini agent does not generate embeddings, deferring to OpenAI")
        return None

    def _error_response(self) -> Dict:
        return {
            "title": "Processing Error",
            "description": "Failed to analyze screenshot with Gemini",
            "tags": ["error"],
            "markdown": "# Error\nFailed to process this screenshot with Gemini."
        }
