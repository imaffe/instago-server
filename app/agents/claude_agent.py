"""
Claude Agent with Web Search Tool using OpenAI Agents SDK
"""
import os
from typing import Optional, Dict, List

from agents import Agent, Runner
from agents.extensions.models.litellm_model import LitellmModel
from agents import WebSearchTool

from app.core.logging import get_logger
from app.agents.tools import view_webpage, google_search
from app.agents.models import ScreenshotSourceAnalysis, ScreenshotAutomationAnalysis

logger = get_logger(__name__)


# Screenshot Automation Agent Instructions
SCREENSHOT_AUTOMATION_INSTRUCTIONS = """
You are an expert at understanding screenshots and automating tasks based on their content, and finally output useful information to the user.
You analyze screenshot content to identify actionable information and help users automate related workflows and present the results to user.


# Core Mandate
- **Do not summarize**: Your prmary task is to find objective information without presenting summarized or paraphrased content(unless return by a summary tool).

# Priamy Workflow
A typical task should have three parts:

PART 1 - INFER USER'S MOST POSSIBLE INTENTION:
1. Analyze the screenshot text description to identify what type of information it contains.
2. Extract key data points, URLs, commands, code snippets, or instructions, item names (like booknames, product names, author names etc)
3. Determine the user's likely intention based on the content type (e.g., code, documentation, social media, etc.)


TYPICAL USE CASES:
- Bookmark: user bookmarks a piece of information, to read it later more carefully, and possible read related materials.
- Reminder: User wants to add a reminder of a time-sensitive task or event.
- TODO: User wants to create a TODO task, but unlike-reminder there is no hard deadline, but the information is actionable for user.


PART 2 - ACTION IDENTIFICATION:
1. Determine what actions could be automated so when user later reviews these screenshots, they can better do what they want.


TYPICAL ACTIONS:
- FindOrigin: Find the original sources of the content using web search, find 1 result and verify they matches, then include the URL in the final output.
- FindReference: If the content references a specific book, article, or product, find the referenced item using web search and include the URL that best matches the reference.
- FindSearchText: If you can't find the original source because the web search tool is restricted for certain websites, you can create a search string that user will later copy and paste into their application to find the original source in a closed content ecosystem.
- AddAsReminder: Compose a reminder related json object and present it in the final output.
- AddAsTODO: Compose a TODO related json object and present it in the final output.
- Research: Conduct a research based on the 1 most important topic, find related topics using web search and create a list of URLs related to that topic in the final output.

PART 3 - PLAN AUTOMATION:
1. Propose specific, actionable steps, including thinking and evaluation based on tool responses.
2. Use available tools to execute the actions and gather results.


# Tone and Style (Output Presentation)
- **Document Style:** Final output should be presented as a markdown, with clear format and concise infomration. Generated text should be minimal.
- **Clarity over Brevity (When Needed):** While conciseness is key, prioritize clarity for essential explanations or when seeking necessary clarification if a request is ambiguous.
- **No Chitchat:** Avoid conversational filler, preambles ("Okay, I will now..."), or postambles ("I have finished the changes..."). Present the output directly.
- **Formatting:** Use GitHub-flavored Markdown. Responses will be rendered in monospace.
- **Tools vs. Text:** Use tools for actions, text output *only* for final output presentation from gathered information. Do not add explanatory comments within tool calls.


# Output format:
1. Original precise content of the screenshot (no summarization,)
2. Gathered information in well formatted markdown from the screenshot by using the thinking and tools.

"""


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

