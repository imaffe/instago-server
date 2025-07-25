"""
Google Custom Search API tool for agents
"""
import os
import httpx

from agents import function_tool
from app.core.logging import get_logger

logger = get_logger(__name__)


@function_tool
def google_search(query: str) -> str:
    """
    Search the web using Google Custom Search API and return formatted results.

    Args:
        query: The search query string extracted directly from screenshot text. Language should be the same.

    Returns:
        Formatted search results as a string
    """
    logger.info(f"Performing Google search for: {query}")
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

        logger.info(f"Google Search API parameters:")
        logger.info(f"  - Query: {query}")
        logger.info(f"  - Search Engine ID: {search_engine_id[:10]}...")  # Log first 10 chars for security
        logger.info(f"  - Number of results: {params['num']}")
        logger.info(f"  - API endpoint: {url}")
        with httpx.Client() as client:
            response = client.get(url, params=params)
            response.raise_for_status()

        data = response.json()
        results = []

        # Parse search results
        if "items" in data:
            logger.info(f"Found {len(data['items'])} search results")
            for i, item in enumerate(data["items"], 1):
                title = item.get("title", "No title")
                link = item.get("link", "")
                snippet = item.get("snippet", "No description")

                results.append(f"{i}. {title}\n   URL: {link}\n   {snippet}\n")
        else:
            logger.info("No search results found in response")

        if results:
            logger.info(f"Returning {len(results)} formatted search results")
            return "\n".join(results)
        else:
            return "No search results found."

    except httpx.HTTPStatusError as e:
        logger.exception(f"Google search HTTP error")
        return f"Error performing Google search: HTTP {e.response.status_code}"
    except Exception as e:
        logger.exception(f"Google search error")
        return f"Error performing search: {str(e)}"
