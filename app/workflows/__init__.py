from app.workflows.openai_agent import OpenAIAgent
from app.workflows.gemini_agent import GeminiAgent
from app.workflows.openrouter_agent import OpenRouterAgent
from app.core.config import settings

# Initialize the appropriate agent based on AGENT_NAME configuration
if settings.AGENT_NAME == "gemini":
    ai_agent = GeminiAgent()
    # If Gemini fails to initialize, fall back to OpenAI
    if not ai_agent.initialized:
        ai_agent = OpenAIAgent()
elif settings.AGENT_NAME == "openrouter":
    ai_agent = OpenRouterAgent()
else:
    ai_agent = OpenAIAgent()

gemini_agent = GeminiAgent()  # Also expose Gemini directly for potential future use
openrouter_agent = OpenRouterAgent()  # Expose OpenRouter agent

__all__ = ["ai_agent", "gemini_agent", "openrouter_agent"]