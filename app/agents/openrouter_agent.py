from typing import Dict

from openai import OpenAI

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class OpenRouterAgent:
    def __init__(self):
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=settings.OPENROUTER_API_KEY,
        )
        self.model = settings.OPENROUTER_MODEL or "qwen/qwen-vl-max"
    
    def process_screenshot(self, base64_image: str) -> Dict:
        try:
            logger.info(f"Processing screenshot with OpenRouter {self.model}")
            
            response = self.client.chat.completions.create(
                extra_headers={
                    "HTTP-Referer": settings.OPENROUTER_SITE_URL or "https://instago.app",
                    "X-Title": settings.OPENROUTER_SITE_NAME or "Instago",
                },
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": """You are a helpful AI assistant analyzing screenshots. 
                        Extract meaningful information and generate:
                        1. A concise title (max 200 chars)
                        2. A detailed description
                        3. Relevant tags as an array
                        4. Markdown formatted content with key information
                        
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
            logger.error(f"Error processing screenshot with OpenRouter: {e}")
            return {
                "title": "Processing Error",
                "description": "Failed to analyze screenshot",
                "tags": ["error"],
                "markdown": "# Error\nFailed to process this screenshot."
            }


openrouter_agent = OpenRouterAgent()