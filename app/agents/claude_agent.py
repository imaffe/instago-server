"""
Claude Agent with Web Search Tool using OpenAI Agents SDK
"""
import os
from typing import Optional
import httpx

from agents import Agent, Runner, function_tool
from agents.extensions.models.litellm_model import LitellmModel

from app.core.logging import get_logger
from app.core.config import settings

logger = get_logger(__name__)


@function_tool
def web_search(query: str) -> str:
    """
    Search the web using DuckDuckGo official API and return formatted results.
    
    Args:
        query: The search query string
        
    Returns:
        Formatted search results as a string
    """
    try:
        results = []
        
        # Use the official DuckDuckGo search API
        with DDGS() as ddgs:
            # Get search results (limit to 5)
            search_results = list(ddgs.text(query, max_results=5))
            
            for i, result in enumerate(search_results, 1):
                title = result.get('title', 'No title')
                url = result.get('href', '')
                snippet = result.get('body', 'No description')
                
                results.append(f"{i}. {title}\n   URL: {url}\n   {snippet}\n")
        
        if results:
            return "\n".join(results)
        else:
            return "No search results found."
            
    except Exception as e:
        logger.error(f"Web search error: {e}")
        return f"Error performing search: {str(e)}"


@function_tool
def google_search(query: str) -> str:
    """
    Search the web using Google Custom Search API and return formatted results.
    
    Args:
        query: The search query string
        
    Returns:
        Formatted search results as a string
    """
    try:
        # Get API credentials from environment or settings
        api_key = os.getenv("GOOGLE_CUSTOM_SEARCH_API_KEY")
        search_engine_id = os.getenv("GOOGLE_CUSTOM_SEARCH_ENGINE_ID")
        
        if not api_key or not search_engine_id:
            logger.warning("Google Custom Search API credentials not configured")
            return "Google Search not available. Please configure GOOGLE_CUSTOM_SEARCH_API_KEY and GOOGLE_CUSTOM_SEARCH_ENGINE_ID."
        
        # Google Custom Search API endpoint
        url = "https://www.googleapis.com/customsearch/v1"
        
        params = {
            "key": api_key,
            "cx": search_engine_id,
            "q": query,
            "num": 5  # Number of results to return (max 10 per request)
        }
        
        with httpx.Client() as client:
            response = client.get(url, params=params)
            response.raise_for_status()
            
        data = response.json()
        results = []
        
        # Parse search results
        if "items" in data:
            for i, item in enumerate(data["items"], 1):
                title = item.get("title", "No title")
                link = item.get("link", "")
                snippet = item.get("snippet", "No description")
                
                results.append(f"{i}. {title}\n   URL: {link}\n   {snippet}\n")
        
        if results:
            return "\n".join(results)
        else:
            return "No search results found."
            
    except httpx.HTTPStatusError as e:
        logger.error(f"Google search HTTP error: {e}")
        return f"Error performing Google search: HTTP {e.response.status_code}"
    except Exception as e:
        logger.error(f"Google search error: {e}")
        return f"Error performing search: {str(e)}"


class ClaudeAgent:
    """Agent powered by Claude model with web search capabilities using OpenAI Agents SDK"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Claude agent using LiteLLM integration
        
        Args:
            api_key: Anthropic API key (optional, will use env var if not provided)
        """
        # Use provided API key or get from environment
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        
        # Create agent with Claude model via LiteLLM
        self.agent = Agent(
            name="Claude Assistant",
            instructions="""You are Claude, a helpful AI assistant with web search capabilities.
            You have access to Google search to find current information.
            
            When a user asks for current information, news, or facts that might have changed recently,
            use the google_search function to find up-to-date information.
            Always provide helpful, accurate, and well-structured responses based on the search results.""",
            model=LitellmModel(
                model="anthropic/claude-sonnet-4",  # Claude Sonnet 4
                api_key=self.api_key
            ) if self.api_key else "litellm/anthropic/claude-sonnet-4",
            tools=[google_search],
        )
        
        logger.info("Claude agent initialized with Google search tool")
        
    async def run_async(self, message: str) -> str:
        """
        Run the agent asynchronously with a user message
        
        Args:
            message: User message to process
            
        Returns:
            Agent's response as a string
        """
        try:
            result = await Runner.run(self.agent, message)
            return result.final_output
                
        except Exception as e:
            logger.error(f"Error running Claude agent: {e}")
            return f"Error: {str(e)}"
            
    def run_sync(self, message: str) -> str:
        """
        Run the agent synchronously with a user message
        
        Args:
            message: User message to process
            
        Returns:
            Agent's response as a string
        """
        try:
            result = Runner.run_sync(self.agent, message)
            return result.final_output
                
        except Exception as e:
            logger.error(f"Error running Claude agent: {e}")
            return f"Error: {str(e)}"


# Example usage
if __name__ == "__main__":
    # Initialize agent
    agent = ClaudeAgent()
    
    # Test direct response
    print("Testing direct response...")
    response = agent.run_sync("What is the capital of France?")
    print("Response:", response)
    
    # Test web search
    print("\nTesting web search...")
    response = agent.run_sync("Search for the latest news about OpenAI agents SDK")
    print("Response:", response)