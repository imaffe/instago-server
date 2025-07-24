import base64
from io import BytesIO
from typing import Dict, List

import numpy as np
from openai import OpenAI
from PIL import Image

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class OpenAIAgent:
    def __init__(self):
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = settings.OPENAI_MODEL
    
    def process_screenshot(self, image_bytes: bytes) -> Dict:
        try:
            base64_image = base64.b64encode(image_bytes).decode('utf-8')
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": """You are an AI assistant that analyzes screenshots and provides rich metadata.
                        Analyze the screenshot and provide:
                        1. A concise title (max 200 chars)
                        2. A detailed description of what you see
                        3. Relevant tags as an array of strings
                        4. Markdown formatted content with key information, insights, and any text found in the image
                        
                        Focus on extracting actionable information, text content, UI elements, and any data shown.
                        
                        Return your response as JSON with keys: title, description, tags, markdown"""
                    },
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": "Analyze this screenshot and provide comprehensive metadata."
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/png;base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ],
                response_format={"type": "json_object"},
                max_tokens=2000,
                temperature=0.3
            )
            
            result = response.choices[0].message.content
            import json
            data = json.loads(result)
            
            return {
                "title": data.get("title", "Untitled Screenshot"),
                "description": data.get("description", ""),
                "tags": data.get("tags", []),
                "markdown": data.get("markdown", "")
            }
            
        except Exception as e:
            logger.error(f"Error processing screenshot with AI: {e}")
            return {
                "title": "Processing Error",
                "description": "Failed to analyze screenshot",
                "tags": ["error"],
                "markdown": "# Error\nFailed to process this screenshot."
            }
    
    def generate_embedding(self, text: str) -> List[float]:
        try:
            response = self.client.embeddings.create(
                model="text-embedding-3-small",
                input=text
            )
            
            return response.data[0].embedding
            
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            return [0.0] * 1536  # Default embedding dimension


openai_agent = OpenAIAgent()