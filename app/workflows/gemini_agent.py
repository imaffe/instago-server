import base64
import json
from typing import Dict

from google import genai
from google.genai import types

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


OUTPUT_SCHEMA = types.Schema(
    type=types.Type.OBJECT,
    properties={
        "general_description": types.Schema(
            type=types.Type.STRING,
            description="A overal description of everything visible in the screenshot"
        ),
        "application": types.Schema(
            type=types.Type.STRING,
            description="Which application, website are the primary focus of the screenshot"
        ),
        "parts": types.Schema(
            type=types.Type.ARRAY,
            items=types.Schema(
                type=types.Type.OBJECT,
                properties={
                    "part_desc": types.Schema(
                        type=types.Type.STRING,
                        description="A short description of what this part contains"
                    ),
                    "type": types.Schema(
                        type=types.Type.STRING,
                        description="Type of content: 'image' or 'text'"
                    ),
                    "location": types.Schema(
                        type=types.Type.STRING,
                        description="Relative location in the image (e.g., 'top-left, 20% width', 'center, full width', 'bottom-right corner')"
                    ),
                    "contents": types.Schema(
                        type=types.Type.ARRAY,
                        items=types.Schema(
                            type=types.Type.OBJECT,
                            properties={
                                "key": types.Schema(
                                    type=types.Type.STRING,
                                    description="The type/category of this content (e.g., 'blog title', 'author name', 'date', 'body')"
                                ),
                                "value": types.Schema(
                                    type=types.Type.STRING,
                                    description="The actual extracted text of the content."
                                )
                            },
                            required=["key", "value"]
                        ),
                        description="Array of key-value pairs representing the content in this part"
                    )
                },
                required=["part_desc", "type", "location", "contents"]
            ),
            description="Array of distinct parts/sections found in the screenshot"
        ),

    },
    required=["general_description", "application", "parts"]
)



class GeminiAgent:
    def __init__(self):
        self.initialized = False
        try:

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

            prompt = """Analyze this screenshot in great detail and provide a comprehensive analysis.

            You must return a well-formatted JSON object with detailed information about everything visible in the screenshot.

            Focus on:
            1. Extract ALL visible text content verbatim (including UI elements, menus, buttons, etc.)
            2. Identify the application, website, or system shown
            3. Describe the visual layout and UI components in detail
            4. Note any code, commands, or technical content
            5. Identify any usernames, timestamps, or metadata
            6. Describe colors, themes, and visual styling
            7. Extract any URLs, file paths, or references
            8. Note the context and purpose of what's being shown
            9. Identify any data, tables, or structured information
            10. Capture any error messages, notifications, or alerts

            Be extremely thorough and detailed in your analysis. Do not summarize - provide complete information.
            """

            config = types.GenerateContentConfig(
                temperature=0.1,  # Lower temperature for more accurate extraction
                max_output_tokens=4096,  # Increased for detailed output
                response_mime_type="application/json",
                response_schema=OUTPUT_SCHEMA
            )

            response = self.client.models.generate_content(
                model=settings.GEMINI_MODEL,
                contents=[
                    types.Part.from_text(text=prompt),
                    types.Part.from_bytes(
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
