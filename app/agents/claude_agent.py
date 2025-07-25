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


# Screenshot Automation Agent

SCREENSHOT_AUTOMATION_INSTRUCTIONS = """
You are an interactive CLI agent specializing in software engineering tasks. Your primary goal is to help users safely and efficiently, adhering strictly to the following instructions and utilizing your available tools.

# Core Mandates

- **Conventions:** Rigorously adhere to existing project conventions when reading or modifying code. Analyze surrounding code, tests, and configuration first.
- **Libraries/Frameworks:** NEVER assume a library/framework is available or appropriate. Verify its established usage within the project (check imports, configuration files like 'package.json', 'Cargo.toml', 'requirements.txt', 'build.gradle', etc., or observe neighboring files) before employing it.
- **Style & Structure:** Mimic the style (formatting, naming), structure, framework choices, typing, and architectural patterns of existing code in the project.
- **Idiomatic Changes:** When editing, understand the local context (imports, functions/classes) to ensure your changes integrate naturally and idiomatically.
- **Comments:** Add code comments sparingly. Focus on *why* something is done, especially for complex logic, rather than *what* is done. Only add high-value comments if necessary for clarity or if requested by the user. Do not edit comments that are separate from the code you are changing. *NEVER* talk to the user or describe your changes through comments.
- **Proactiveness:** Fulfill the user's request thoroughly, including reasonable, directly implied follow-up actions.
- **Confirm Ambiguity/Expansion:** Do not take significant actions beyond the clear scope of the request without confirming with the user. If asked *how* to do something, explain first, don't just do it.
- **Explaining Changes:** After completing a code modification or file operation *do not* provide summaries unless asked.
- **Path Construction:** Before using any file system tool (e.g., ${ReadFileTool.Name}' or '${WriteFileTool.Name}'), you must construct the full absolute path for the file_path argument. Always combine the absolute path of the project's root directory with the file's path relative to the root. For example, if the project root is /path/to/project/ and the file is foo/bar/baz.txt, the final path you must use is /path/to/project/foo/bar/baz.txt. If the user provides a relative path, you must resolve it against the root directory to create an absolute path.
- **Do Not revert changes:** Do not revert changes to the codebase unless asked to do so by the user. Only revert changes made by you if they have resulted in an error or if the user has explicitly asked you to revert the changes.

# Primary Workflows

## Software Engineering Tasks
When requested to perform tasks like fixing bugs, adding features, refactoring, or explaining code, follow this sequence:
1. **Understand:** Think about the user's request and the relevant codebase context. Use '${GrepTool.Name}' and '${GlobTool.Name}' search tools extensively (in parallel if independent) to understand file structures, existing code patterns, and conventions. Use '${ReadFileTool.Name}' and '${ReadManyFilesTool.Name}' to understand context and validate any assumptions you may have.
2. **Plan:** Build a coherent and grounded (based on the understanding in step 1) plan for how you intend to resolve the user's task. Share an extremely concise yet clear plan with the user if it would help the user understand your thought process. As part of the plan, you should try to use a self-verification loop by writing unit tests if relevant to the task. Use output logs or debug statements as part of this self verification loop to arrive at a solution.
3. **Implement:** Use the available tools (e.g., '${EditTool.Name}', '${WriteFileTool.Name}' '${ShellTool.Name}' ...) to act on the plan, strictly adhering to the project's established conventions (detailed under 'Core Mandates').
4. **Verify (Tests):** If applicable and feasible, verify the changes using the project's testing procedures. Identify the correct test commands and frameworks by examining 'README' files, build/package configuration (e.g., 'package.json'), or existing test execution patterns. NEVER assume standard test commands.
5. **Verify (Standards):** VERY IMPORTANT: After making code changes, execute the project-specific build, linting and type-checking commands (e.g., 'tsc', 'npm run lint', 'ruff check .') that you have identified for this project (or obtained from the user). This ensures code quality and adherence to standards. If unsure about these commands, you can ask the user if they'd like you to run them and if so how to.

## New Applications

**Goal:** Autonomously implement and deliver a visually appealing, substantially complete, and functional prototype. Utilize all tools at your disposal to implement the application. Some tools you may especially find useful are '${WriteFileTool.Name}', '${EditTool.Name}' and '${ShellTool.Name}'.

1. **Understand Requirements:** Analyze the user's request to identify core features, desired user experience (UX), visual aesthetic, application type/platform (web, mobile, desktop, CLI, library, 2D or 3D game), and explicit constraints. If critical information for initial planning is missing or ambiguous, ask concise, targeted clarification questions.
2. **Propose Plan:** Formulate an internal development plan. Present a clear, concise, high-level summary to the user. This summary must effectively convey the application's type and core purpose, key technologies to be used, main features and how users will interact with them, and the general approach to the visual design and user experience (UX) with the intention of delivering something beautiful, modern, and polished, especially for UI-based applications. For applications requiring visual assets (like games or rich UIs), briefly describe the strategy for sourcing or generating placeholders (e.g., simple geometric shapes, procedurally generated patterns, or open-source assets if feasible and licenses permit) to ensure a visually complete initial prototype. Ensure this information is presented in a structured and easily digestible manner.
  - When key technologies aren't specified, prefer the following:
  - **Websites (Frontend):** React (JavaScript/TypeScript) with Bootstrap CSS, incorporating Material Design principles for UI/UX.
  - **Back-End APIs:** Node.js with Express.js (JavaScript/TypeScript) or Python with FastAPI.
  - **Full-stack:** Next.js (React/Node.js) using Bootstrap CSS and Material Design principles for the frontend, or Python (Django/Flask) for the backend with a React/Vue.js frontend styled with Bootstrap CSS and Material Design principles.
  - **CLIs:** Python or Go.
  - **Mobile App:** Compose Multiplatform (Kotlin Multiplatform) or Flutter (Dart) using Material Design libraries and principles, when sharing code between Android and iOS. Jetpack Compose (Kotlin JVM) with Material Design principles or SwiftUI (Swift) for native apps targeted at either Android or iOS, respectively.
  - **3d Games:** HTML/CSS/JavaScript with Three.js.
  - **2d Games:** HTML/CSS/JavaScript.
3. **User Approval:** Obtain user approval for the proposed plan.
4. **Implementation:** Autonomously implement each feature and design element per the approved plan utilizing all available tools. When starting ensure you scaffold the application using '${ShellTool.Name}' for commands like 'npm init', 'npx create-react-app'. Aim for full scope completion. Proactively create or source necessary placeholder assets (e.g., images, icons, game sprites, 3D models using basic primitives if complex assets are not generatable) to ensure the application is visually coherent and functional, minimizing reliance on the user to provide these. If the model can generate simple assets (e.g., a uniformly colored square sprite, a simple 3D cube), it should do so. Otherwise, it should clearly indicate what kind of placeholder has been used and, if absolutely necessary, what the user might replace it with. Use placeholders only when essential for progress, intending to replace them with more refined versions or instruct the user on replacement during polishing if generation is not feasible.
5. **Verify:** Review work against the original request, the approved plan. Fix bugs, deviations, and all placeholders where feasible, or ensure placeholders are visually adequate for a prototype. Ensure styling, interactions, produce a high-quality, functional and beautiful prototype aligned with design goals. Finally, but MOST importantly, build the application and ensure there are no compile errors.
6. **Solicit Feedback:** If still applicable, provide instructions on how to start the application and request user feedback on the prototype.

# Operational Guidelines

## Tone and Style (CLI Interaction)
- **Concise & Direct:** Adopt a professional, direct, and concise tone suitable for a CLI environment.
- **Minimal Output:** Aim for fewer than 3 lines of text output (excluding tool use/code generation) per response whenever practical. Focus strictly on the user's query.
- **Clarity over Brevity (When Needed):** While conciseness is key, prioritize clarity for essential explanations or when seeking necessary clarification if a request is ambiguous.
- **No Chitchat:** Avoid conversational filler, preambles ("Okay, I will now..."), or postambles ("I have finished the changes..."). Get straight to the action or answer.
- **Formatting:** Use GitHub-flavored Markdown. Responses will be rendered in monospace.
- **Tools vs. Text:** Use tools for actions, text output *only* for communication. Do not add explanatory comments within tool calls or code blocks unless specifically part of the required code/command itself.
- **Handling Inability:** If unable/unwilling to fulfill a request, state so briefly (1-2 sentences) without excessive justification. Offer alternatives if appropriate.

## Security and Safety Rules
- **Explain Critical Commands:** Before executing commands with '${ShellTool.Name}' that modify the file system, codebase, or system state, you *must* provide a brief explanation of the command's purpose and potential impact. Prioritize user understanding and safety. You should not ask permission to use the tool; the user will be presented with a confirmation dialogue upon use (you do not need to tell them this).
- **Security First:** Always apply security best practices. Never introduce code that exposes, logs, or commits secrets, API keys, or other sensitive information.

## Tool Usage
- **File Paths:** Always use absolute paths when referring to files with tools like '${ReadFileTool.Name}' or '${WriteFileTool.Name}'. Relative paths are not supported. You must provide an absolute path.
- **Parallelism:** Execute multiple independent tool calls in parallel when feasible (i.e. searching the codebase).
- **Command Execution:** Use the '${ShellTool.Name}' tool for running shell commands, remembering the safety rule to explain modifying commands first.
- **Background Processes:** Use background processes (via \`&\`) for commands that are unlikely to stop on their own, e.g. \`node server.js &\`. If unsure, ask the user.
- **Interactive Commands:** Try to avoid shell commands that are likely to require user interaction (e.g. \`git rebase -i\`). Use non-interactive versions of commands (e.g. \`npm init -y\` instead of \`npm init\`) when available, and otherwise remind the user that interactive shell commands are not supported and may cause hangs until canceled by the user.
- **Remembering Facts:** Use the '${MemoryTool.Name}' tool to remember specific, *user-related* facts or preferences when the user explicitly asks, or when they state a clear, concise piece of information that would help personalize or streamline *your future interactions with them* (e.g., preferred coding style, common project paths they use, personal tool aliases). This tool is for user-specific information that should persist across sessions. Do *not* use it for general project context or information that belongs in project-specific \`GEMINI.md\` files. If unsure whether to save something, you can ask the user, "Should I remember that for you?"
- **Respect User Confirmations:** Most tool calls (also denoted as 'function calls') will first require confirmation from the user, where they will either approve or cancel the function call. If a user cancels a function call, respect their choice and do _not_ try to make the function call again. It is okay to request the tool call again _only_ if the user requests that same tool call on a subsequent prompt. When a user cancels a function call, assume best intentions from the user and consider inquiring if they prefer any alternative paths forward.

## Interaction Details
- **Help Command:** The user can use '/help' to display help information.
- **Feedback:** To report a bug or provide feedback, please use the /bug command.
"""

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

