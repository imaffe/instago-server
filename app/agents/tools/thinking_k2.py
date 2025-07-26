"""
K2 thinking tool for agents to reason through complex tasks using Moonshot Kimi K2 model
"""
from openai import OpenAI

from agents import function_tool
from app.core.logging import get_logger
from app.core.config import settings

logger = get_logger(__name__)


@function_tool
def think_with_k2(current_context: str, question: str) -> str:
    """
    Use Kimi K2 model to think through a problem and generate a detailed plan.

    Args:
        current_context: The current state/context of the analysis
        question: What specific question or task to think about

    Returns:
        K2's reasoning and plan as a string
    """
    logger.info(f"K2 thinking about: {question[:100]}...")

    try:
        # Check if K2 is configured
        if not settings.MOONSHOT_API_KEY:
            logger.warning("Moonshot API key not configured")
            return "K2 thinking tool not available. Please configure MOONSHOT_API_KEY."
        
        # Initialize OpenAI client with Moonshot config
        client = OpenAI(
            api_key=settings.MOONSHOT_API_KEY,
            base_url=settings.MOONSHOT_BASE_URL
        )
        
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
        
        # System prompt for K2
        system_prompt = """You are an expert reasoning assistant. You excel at breaking down complex problems, 
analyzing information systematically, and creating detailed action plans. You are particularly good at 
understanding context from screenshots and identifying the most relevant information to search for."""
        
        logger.info("Sending request to K2 for thinking")
        
        # Make the API call with K2 model
        completion = client.chat.completions.create(
            model=settings.MOONSHOT_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": thinking_prompt}
            ],
            temperature=0.6,  # As recommended in the Moonshot docs
            max_tokens=20000
        )
        
        thinking_output = completion.choices[0].message.content or "No thinking output"
        logger.info(f"K2 thinking complete. Output length: {len(thinking_output)}")
        
        return thinking_output
        
    except Exception as e:
        logger.exception(f"Error in K2 thinking tool")
        return f"Error in K2 thinking process: {str(e)}"