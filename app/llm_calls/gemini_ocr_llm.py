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
        "extracted_highlight_text": types.Schema(
            type=types.Type.STRING,
            description="The part of text you think are the most important part of the image."
        ),

    },
    required=["general_description", "application", "parts", "extracted_highlight_text"]
)



class GeminiOCRLLM:
    def __init__(self):
        self.initialized = False
        try:

            self.client = genai.Client()
            self.initialized = True
            logger.info("Gemini OCR LLM initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Gemini OCR LLM: {e}")
            self.initialized = False

    def process_screenshot(self, base64_image: str) -> Dict:
        if not self.initialized:
            logger.error("Gemini OCR LLM not initialized")
            return self._error_response()

        try:
            # Decode base64 image
            image_bytes = base64.b64decode(base64_image)

            prompt = """Analyze this screenshot and extract all information in a structured format.

            Your response must follow this structure:

            1. **general_description**: Provide a comprehensive overview of everything visible in the screenshot. Include the overall context, purpose, and what the user is looking at.

            2. **application**: Identify the primary MacOS application (If Browser, identify the website) shown in the screenshot. Be specific (e.g. "X", "GitHub", "Medium", "Reddit", "Hackernews").

            3. **parts**: Break down the screenshot into distinct sections or areas. For each part:
               - **part_desc**: Describe what this section contains
               - **type**: Whether it's primarily 'text' or 'image' content
               - **location**: Where it appears (e.g., "top navigation bar", "main content area", "sidebar")
               - **contents**: Extract ALL OCR text as key-value pairs. The language should not be changed. The key is the type/category of this content like "title", "body_content", and the value is the actual OCR extracted text.
                 - For text content: use descriptive keys like "heading", "paragraph", "button_text", "menu_item", etc.
                 - For metadata: use "author", "timestamp", "username", etc.
                 - Extract the "value" verbatim - do not summarize or paraphrase.

            4. **extracted_highlight_text**: Identify the most important text from "content" value (OCR text). This should be the key information that users would most likely want to save or reference later. Examples:


            Important guidelines:
            - Extract ALL major visible text, including UI elements, menus, buttons, labels.

            - Be thorough - every piece of text should be captured in the appropriate part.
            - Group related content logically into parts (e.g., navigation bar, main content, sidebar)
            - Describe relative locations of each parts.
            - Provide a concise description of what each part does in part_desc.
            """

            config = types.GenerateContentConfig(
                temperature=0.1,  # Lower temperature for more accurate extraction
                max_output_tokens=8000,  # Increased for detailed output
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
            if response.text:
                result = json.loads(response.text)
            else:
                raise ValueError("Empty response from Gemini")

            # Return the full JSON result from Gemini
            return result

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
