import base64
import json
from typing import Dict

from google import genai
from google.genai.types import GenerateContentConfig, Part

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class GeminiAgent:
    def __init__(self):
        self.initialized = False
        try:
            # Initialize Google GenAI client
            # Uses environment variables:
            # - GOOGLE_CLOUD_PROJECT or falls back to VERTEX_AI_PROJECT setting
            # - GOOGLE_CLOUD_LOCATION or falls back to VERTEX_AI_LOCATION setting
            # - GOOGLE_GENAI_USE_VERTEXAI=True to use Vertex AI
            self.client = genai.Client()
            self.initialized = True
            logger.info("Gemini agent initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Gemini agent: {e}")
            self.initialized = False

    def process_screenshot(self, base64_image: str) -> Dict:
        if not self.initialized:
            logger.error("Gemini agent not initialized")
            return self._error_response()

        try:
            # Decode base64 image
            image_bytes = base64.b64decode(base64_image)

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

            config = GenerateContentConfig(
                temperature=0.3,
                max_output_tokens=2048,
                response_mime_type="application/json",
                response_schema={
                    "type": "object",
                    "properties": {
                        "title": {
                            "type": "string",
                            "description": "A concise, descriptive title (max 200 chars)"
                        },
                        "description": {
                            "type": "string", 
                            "description": "A detailed description of what's shown"
                        },
                        "tags": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Relevant tags for categorization"
                        },
                        "markdown": {
                            "type": "string",
                            "description": "Rich markdown documentation with summary, key info, and insights"
                        }
                    },
                    "required": ["title", "description", "tags", "markdown"]
                }
            )

            response = self.client.models.generate_content(
                model=settings.GEMINI_MODEL,
                contents=[
                    Part.from_text(prompt),
                    Part.from_bytes(
                        data=image_bytes,
                        mime_type="image/png"
                    )
                ],
                config=config
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
            logger.error(f"L: {e}")
            return self._error_response()
        except Exception as e:
            logger.error(f"Error processing screenshot with Gemini: {e}")
            return self._error_response()

    def _error_response(self) -> Dict:
        return {
            "title": "Processing Error",
            "description": "Failed to analyze screenshot with Gemini",
            "tags": ["error"],
            "markdown": "# Error\nFailed to process this screenshot with Gemini."
        }
