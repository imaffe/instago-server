"""
Web viewer tool for agents to view and extract content from webpages
"""
import httpx
from bs4 import BeautifulSoup

from agents import function_tool
from app.core.logging import get_logger

logger = get_logger(__name__)


@function_tool
def view_webpage(url: str) -> str:
    """
    View and extract text content from a webpage.

    Args:
        url: The URL of the webpage to view

    Returns:
        Extracted text content from the webpage or error message
    """
    logger.info(f"Attempting to view webpage: {url}")
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }

        with httpx.Client(follow_redirects=True, timeout=10.0) as client:
            logger.info(f"Sending GET request to {url}")
            response = client.get(url, headers=headers)
            response.raise_for_status()
            logger.info(f"Successfully fetched {url} - Status: {response.status_code}")

        # Parse HTML content
        soup = BeautifulSoup(response.text, 'html.parser')

        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()

        # Get text content
        text = soup.get_text()

        # Clean up text
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = ' '.join(chunk for chunk in chunks if chunk)

        # Limit text length to avoid token limits
        max_length = 3000
        original_length = len(text)
        if original_length > max_length:
            text = text[:max_length] + "... [truncated]"
            logger.info(f"Truncated webpage content from {original_length} to {max_length} chars")
        else:
            logger.info(f"Extracted {original_length} chars from webpage")

        return f"Content from {url}:\n{text}"

    except httpx.HTTPStatusError as e:
        logger.warning(f"HTTP error {e.response.status_code} when accessing {url}")
        return f"HTTP error {e.response.status_code} when accessing {url}"
    except Exception as e:
        logger.exception(f"Error viewing webpage {url}")
        return f"Error viewing webpage: {str(e)}"