"""
Claude Agent with Web Search Tool using OpenAI Agents SDK
"""
import os
from typing import Optional, Dict, List

from agents import Agent, Runner, trace
from agents.extensions.models.litellm_model import LitellmModel

from app.core.logging import get_logger
from app.agents.tools import view_webpage, google_search

logger = get_logger(__name__)


# Screenshot Automation Agent Instructions
SCREENSHOT_AUTOMATION_INSTRUCTIONS = """
You are an expert at understanding screenshots and automating tasks based on their content, and finally output useful information to the user.
You analyze screenshot content to identify actionable information and help users automate related workflows and present the results to user.


# Core Mandate

- **Use OCR text unchanged for original source search**: Always use the text extracted directly from the screenshot in its original format, especially keeping the original language and not translating it.
- **Do not summarize**: Your prmary task is to find objective information.  Try not to summarize or paraphrase content(unless return by a summary tool) as much as possible.

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
- FindOrigin: Find the original sources of the content using web search. Always use text directly from the OCR text. Find 1 result and verify they matches, then include the final URL in the final output.
- FindReference: If the content references a specific book, article, or product, find the referenced item using web search and include the URL that best matches the reference.
- FindSearchText: If you can't find the original source because the web search tool is restricted for certain websites, you can create a search string that user will later copy and paste into their application to find the original source in a closed content ecosystem.
- AddAsReminder: Compose a reminder related json object and present it in the final output.
- AddAsTODO: Compose a TODO related json object and present it in the final output.
- Research: Conduct a research based on the 1 most important topic, find related topics using web search and create a list of URLs related to that topic in the final output.


TOOLS:(
- **Google Search**: Use this tool to find the original source of the content or related information. Always use the text directly from the screenshot in the original format, especially keep the original language and do not translate.
- **View Webpage**: Use this tool to view the content of a webpage when you have found a relevant URL. This helps verify the content and extract additional information if needed.

PART 3 - PLAN AUTOMATION:
1. Propose specific, actionable steps, including thinking and evaluation based on tool responses.
2. Show detailed reasoning for each step, including how you arrived at the actions and what tool you will use to complete the action, and what arguments you should give to the tool.
3. Use available tools to execute the actions and gather results.


# Tone and Style (Output Presentation)
- **Document Style:** Final output should be presented as a markdown, with clear format and concise infomration. Generated text should be minimal.
- **Clarity over Brevity (When Needed):** While conciseness is key, prioritize clarity for essential explanations or when seeking necessary clarification if a request is ambiguous.
- **No Chitchat:** Avoid conversational filler, preambles ("Okay, I will now..."), or postambles ("I have finished the changes..."). Present the output directly.
- **Formatting:** Use GitHub-flavored Markdown. Responses will be rendered in monospace.
- **Tools vs. Text:** Use tools for actions, text output *only* for final output presentation from gathered information. Do not add explanatory comments within tool calls.


# Final Output format:
1. Original precise content of the screenshot (no summarization)
2. Include the extracted body texts you think are the most relevant for the user in the markdown.
3. Gathered information in well formatted markdown from the screenshot by using the thinking and tools.

"""


SCREENSHOT_AUTOMATION_USER_INSTRUCTIONS = """Analyze this screenshot data and find useful information:

Application: {application}
General Description: {general_description}

Parts:
{parts_formatted}

Based on this structured information, research and find relevant sources, references, or additional information that would be useful for the user."""


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

    def _format_parts(self, parts: List[Dict]) -> str:
        """Format the parts array into a readable string"""
        formatted_parts = []
        for i, part in enumerate(parts, 1):
            part_text = f"\n{i}. {part.get('part_desc', 'Unknown part')}"
            part_text += f"\n   Type: {part.get('type', 'unknown')}"
            part_text += f"\n   Location: {part.get('location', 'unknown')}"

            contents = part.get('contents', [])
            if contents:
                part_text += "\n   Contents:"
                for content in contents:
                    key = content.get('key', 'unknown')
                    value = content.get('value', '')
                    # Truncate very long values for readability
                    if len(value) > 200:
                        value = value[:200] + "..."
                    part_text += f"\n     - {key}: {value}"

            formatted_parts.append(part_text)

        return "\n".join(formatted_parts)

    async def find_screenshot_source(self, screenshot_info: dict) -> str:
        logger.info("Starting screenshot source finding")
        logger.info(f"Screenshot info - Application: {screenshot_info.get('application', 'Unknown')}")
        logger.info(f"Screenshot info - Parts count: {len(screenshot_info.get('parts', []))}")

        try:
            logger.info("Creating unified analyzer and source finder agent with structured output")

            analyzer_finder = Agent(
                name="Screenshot Analyzer and Source Finder",
                instructions=SCREENSHOT_AUTOMATION_INSTRUCTIONS,
                model=LitellmModel(
                    model="anthropic/claude-sonnet-4-20250514",
                    api_key=self.api_key
                ) if self.api_key else "litellm/anthropic/claude-sonnet-4-20250514",
                tools=[google_search, view_webpage]
            )

            # Format the parts array for the prompt
            parts_formatted = self._format_parts(screenshot_info.get('parts', []))

            # Construct the search prompt
            prompt = SCREENSHOT_AUTOMATION_USER_INSTRUCTIONS.format(
                application=screenshot_info.get('application', 'Unknown'),
                general_description=screenshot_info.get('general_description', ''),
                parts_formatted=parts_formatted
            )

            logger.info(f"Running analyzer-finder with prompt length: {len(prompt)}")

            # Use trace to capture the entire workflow
            with trace("Screenshot Analysis Workflow") as workflow_trace:
                # Run the unified analyzer and source finder
                result = await Runner.run(analyzer_finder, prompt)

                # Log trace information
                logger.info(f"=== Trace Information ===")
                logger.info(f"Trace ID: {workflow_trace.trace_id}")

                # Get the markdown output directly
                markdown_output = result.final_output
                logger.info(f"\n=== Final Output ===")
                logger.info(f"Output length: {len(markdown_output)}")
                logger.info(f"Output preview: {markdown_output[:500]}...")

            return markdown_output

        except Exception as e:
            logger.exception("Error finding screenshot source")
            return f"# Error\n\nFailed to analyze screenshot: {str(e)}"

    def find_screenshot_source_sync(self, screenshot_info: dict) -> str:
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

