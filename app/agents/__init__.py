from app.agents.screenshot_agent import ScreenshotAgent
from app.agents.gemini_agent import GeminiAgent
from app.core.config import settings

# Initialize the appropriate agent based on configuration
if settings.USE_GEMINI_FOR_SCREENSHOTS and settings.VERTEX_AI_PROJECT:
    ai_agent = GeminiAgent()
    # If Gemini fails to initialize, fall back to OpenAI
    if not ai_agent.initialized:
        ai_agent = ScreenshotAgent()
else:
    ai_agent = ScreenshotAgent()

gemini_agent = GeminiAgent()  # Also expose Gemini directly for potential future use

__all__ = ["ai_agent", "gemini_agent"]