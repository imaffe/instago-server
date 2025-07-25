"""
Claude Agent with Web Search Tool using OpenAI Agents SDK
"""
import os
from typing import Optional, Dict, List

from agents import Agent, Runner
from agents.extensions.models.litellm_model import LitellmModel
from agents import WebSearchTool
from pydantic import BaseModel, Field

from app.core.logging import get_logger
from app.agents.tools import view_webpage, google_search

logger = get_logger(__name__)


# Pydantic Models for Structured Output
class ScreenshotSourceAnalysis(BaseModel):
    """Model for unified screenshot analysis and source finding"""
    # Analysis fields
    analysis_summary: str = Field(description="Brief summary of what the screenshot contains")
    key_entities: List[str] = Field(description="Key entities found (usernames, websites, product names, etc)")
    content_type: str = Field(description="Type of content: 'social_media', 'article', 'documentation', 'chat', 'code', 'other'")

    # Source finding fields
    original_source: Optional[str] = Field(description="The URL of the original source, or None if not found")
    confidence: str = Field(description="Confidence level: 'high', 'medium', or 'low'")
    verification: bool = Field(description="Whether the source was verified by viewing the webpage")
    reasoning: str = Field(description="Detailed explanation of how the source was found and why this confidence level")
    alternative_sources: List[str] = Field(description="List of alternative possible sources if main source is uncertain")


# Agent Instructions
SCREENSHOT_ANALYZER_INSTRUCTIONS = """You are an expert at analyzing screenshots and finding their original sources.

Your task is to:
1. Extract and analyze all text and visual content from the screenshot
2. Provide a descriptive title and detailed description
3. Generate relevant tags for categorization
4. Create comprehensive markdown documentation
5. Search for and verify the original source of the content

For source finding, focus on:
- Twitter/X posts (look for @usernames, tweet patterns, "View on X" text)
- Hacker News posts (look for HN styling, comment patterns, "points by" text)
- Reddit posts (look for subreddit names, upvote patterns, "Posted by u/" text)
- Blog posts (look for article titles, author names, publication dates)
- News articles (look for headlines, publication names, journalist bylines)
- GitHub issues/PRs (look for issue numbers, usernames, repo names)

Search strategy:
1. Identify unique phrases or quotes from the screenshot
2. Search for exact matches or key phrases
3. If you find potential sources, verify them by viewing the webpage
4. Confirm the content matches what's in the screenshot

Confidence levels:
- "high": Found and verified the exact source with matching content
- "medium": Found a likely source but couldn't fully verify
- "low": Found possible sources but uncertain
- "none": Could not find any source

Always provide the most useful and actionable information possible."""

SCREENSHOT_SOURCE_FINDER_INSTRUCTIONS = """You are an expert at analyzing screenshots and finding their original sources from the web.
You will receive OCR text and metadata from a screenshot.

Your task has two parts:

PART 1 - ANALYSIS:
1. Analyze the content to understand what type of content this is
2. Identify key entities, phrases, usernames, or unique identifiers
3. Determine the content type (social media, article, documentation, etc)

PART 2 - SOURCE FINDING:
1. Based on your analysis, search for the original source
2. Use the identified key phrases and entities in your search
3. Verify any found sources by viewing the webpage
4. Determine your confidence level based on verification

Content type patterns to look for:
- Twitter/X: @usernames, retweet/like counts, "View on X", Twitter UI elements
- Hacker News: orange header, "points by", comment threading, HN domain
- Reddit: subreddit names, upvote counts, "Posted by u/", Reddit UI
- GitHub: issue/PR numbers, commit hashes, file paths, GitHub UI
- Blog posts: article titles, author bylines, publication dates, blog layouts
- News articles: headlines, news outlet names, journalist names, article structure
- Documentation: technical content, code examples, API references, doc layouts
- Chat/Discord: message timestamps, usernames with discriminators, chat UI

Search strategy:
1. Use exact quotes for unique phrases
2. Combine key entities with content type (e.g., "username site:twitter.com")
3. Try multiple search variations if first attempt fails
4. Always verify by viewing the actual webpage

Confidence levels:
- "high": Found and verified exact source with all content matching
- "medium": Found likely source but some details differ or couldn't fully verify
- "low": Found possible sources but uncertain, multiple candidates, or no verification

If you find multiple possible sources, list them in alternative_sources.
Always explain your reasoning thoroughly."""

# Prompt Templates
SCREENSHOT_SOURCE_SEARCH_PROMPT = """Analyze and find the original source of this screenshot:

Title: {title}
Description: {description}
Tags: {tags}

OCR and Content:
{markdown}

First analyze the content to understand what it is, then search for the original source.
Verify any sources you find by viewing the webpage. Provide your complete structured analysis."""


class ClaudeAgent:
    """Agent powered by Claude model with web search capabilities using OpenAI Agents SDK"""

    def __init__(self, api_key: Optional[str] = None):
        logger.info("Initializing Claude agent")
        # Use provided API key or get from environment
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        self.initialized = False

        if not self.api_key:
            logger.warning("No Anthropic API key provided, agent may not function properly")
        else:
            logger.info("Anthropic API key found")
            self.initialized = True

    async def find_screenshot_source(self, screenshot_info: dict) -> dict:
        logger.info("Starting screenshot source finding")
        logger.info(f"Screenshot info - Title: {screenshot_info.get('title', 'Unknown')}")
        logger.info(f"Screenshot info - Tags: {screenshot_info.get('tags', [])}")

        try:
            logger.info("Creating unified analyzer and source finder agent with structured output")

            # Create instance of WebSearchTool
            web_search_tool = WebSearchTool()

            analyzer_finder = Agent(
                name="Screenshot Analyzer and Source Finder",
                instructions=SCREENSHOT_SOURCE_FINDER_INSTRUCTIONS,
                model=LitellmModel(
                    model="anthropic/claude-sonnet-4-20250514",
                    api_key=self.api_key
                ) if self.api_key else "litellm/anthropic/claude-sonnet-4-20250514",
                tools=[google_search, view_webpage],  # Using WebSearchTool instead of google_search
                output_type=ScreenshotSourceAnalysis
            )

            # Construct the search prompt
            prompt = SCREENSHOT_SOURCE_SEARCH_PROMPT.format(
                title=screenshot_info.get('title', 'Unknown'),
                description=screenshot_info.get('description', ''),
                tags=', '.join(screenshot_info.get('tags', [])),
                markdown=screenshot_info.get('markdown', '')
            )

            logger.info(f"Running analyzer-finder with prompt length: {len(prompt)}")
            # Run the unified analyzer and source finder
            result = await Runner.run(analyzer_finder, prompt)

            # Get structured output directly from agent
            try:
                output = result.final_output_as(ScreenshotSourceAnalysis)
                result_dict = {
                    "original_source": output.original_source,
                    "confidence": output.confidence,
                    "verification": output.verification,
                    "details": output.reasoning,
                    "analysis_summary": output.analysis_summary,
                    "key_entities": output.key_entities,
                    "content_type": output.content_type,
                    "alternative_sources": output.alternative_sources
                }
                logger.info(f"Got structured output - URL: {output.original_source}, Confidence: {output.confidence}, Type: {output.content_type}")
            except Exception as parse_error:
                # Fallback: try to parse JSON from text response
                logger.warning(f"Could not get structured output: {parse_error}, trying JSON parse")
                import json
                try:
                    response_text = result.final_output
                    # Look for JSON in the response
                    json_start = response_text.find('{')
                    json_end = response_text.rfind('}') + 1
                    if json_start >= 0 and json_end > json_start:
                        json_str = response_text[json_start:json_end]
                        parsed = json.loads(json_str)
                        result_dict = {
                            "original_source": parsed.get("original_source"),
                            "confidence": parsed.get("confidence", "low"),
                            "verification": parsed.get("verification", False),
                            "details": parsed.get("reasoning", response_text),
                            "analysis_summary": parsed.get("analysis_summary", ""),
                            "key_entities": parsed.get("key_entities", []),
                            "content_type": parsed.get("content_type", "other"),
                            "alternative_sources": parsed.get("alternative_sources", [])
                        }
                    else:
                        raise ValueError("No JSON found in response")
                except Exception as json_error:
                    logger.error(f"JSON parse failed: {json_error}")
                    # Last resort: return the raw response
                    result_dict = {
                        "original_source": None,
                        "confidence": "low",
                        "verification": False,
                        "details": result.final_output,
                        "analysis_summary": "",
                        "key_entities": [],
                        "content_type": "other",
                        "alternative_sources": []
                    }

            logger.info(f"Returning source result - URL: {result_dict['original_source']}, Confidence: {result_dict['confidence']}, Verified: {result_dict['verification']}")
            return result_dict

        except Exception as e:
            logger.exception("Error finding screenshot source")
            return {
                "original_source": None,
                "confidence": "error",
                "verification": False,
                "details": f"Error: {str(e)}"
            }

    def find_screenshot_source_sync(self, screenshot_info: dict) -> dict:
        """
        Synchronous version of find_screenshot_source.
        """
        logger.info("Running find_screenshot_source in sync mode")
        import asyncio
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            logger.info("Creating new event loop for sync execution")
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        return loop.run_until_complete(self.find_screenshot_source(screenshot_info))

    def _error_response(self) -> Dict:
        """Return a standard error response"""
        return {
            "title": "Processing Error",
            "description": "Failed to analyze screenshot with Claude",
            "tags": ["error"],
            "markdown": "# Error\nFailed to process this screenshot with Claude.",
            "original_source": None,
            "source_confidence": "none",
            "source_verified": False,
            "source_details": "An error occurred during processing"
        }

