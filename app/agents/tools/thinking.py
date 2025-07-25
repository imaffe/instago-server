"""
Thinking tool for agents to reason through complex tasks
"""
import os
from typing import Dict
import httpx

from agents import function_tool
from app.core.logging import get_logger

logger = get_logger(__name__)


@function_tool
def think_and_plan(current_context: str, question: str) -> str:
    """
    Use Claude to think through a problem and generate a detailed plan.

    Args:
        current_context: The current state/context of the analysis
        question: What specific question or task to think about

    Returns:
        Claude's reasoning and plan as a string
    """
    logger.info(f"Thinking about: {question[:100]}...")

    try:
        # Get Anthropic API key
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            logger.warning("Anthropic API key not configured")
            return "Thinking tool not available. Please configure ANTHROPIC_API_KEY."

        # Prepare the thinking prompt
        thinking_prompt = f"""You are a reasoning assistant helping to analyze screenshots and find information.

Current Context:
{current_context}

Question/Task:
{question}

Please think through this step-by-step and provide:
1. Your understanding of the current situation
2. What information we have so far
3. What we still need to find
4. A detailed plan of action with specific steps
5. Which tools to use and with what arguments
6. Expected outcomes and fallback strategies
7. Include thinking process in the final output

Be specific and detailed in your reasoning."""

        # Call Claude API directly
        headers = {
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json"
        }

        data = {
            "model": "claude-sonnet-4-20250514",
            "max_tokens": 20000,
            "temperature": 0.7,
            "messages": [
                {
                    "role": "user",
                    "content": thinking_prompt
                }
            ]
        }

        logger.info("Sending request to Claude for thinking")
        with httpx.Client() as client:
            response = client.post(
                "https://api.anthropic.com/v1/messages",
                headers=headers,
                json=data,
                timeout=30.0
            )
            response.raise_for_status()

        result = response.json()
        thinking_output = result.get("content", [{}])[0].get("text", "No thinking output")

        logger.info(f"Thinking complete. Output length: {len(thinking_output)}")
        return thinking_output

    except httpx.HTTPStatusError as e:
        logger.exception(f"Claude API HTTP error")
        return f"Error in thinking process: HTTP {e.response.status_code}"
    except Exception as e:
        logger.exception(f"Error in thinking tool")
        return f"Error in thinking process: {str(e)}"
