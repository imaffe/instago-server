TITLE: Run a Basic OpenAI Agent to Generate Text
DESCRIPTION: Demonstrates how to initialize an OpenAI Agent with specific instructions and run it synchronously to generate a creative text output. This example requires the 'OPENAI_API_KEY' environment variable to be set for authentication with the OpenAI API.
SOURCE: https://github.com/openai/openai-agents-python/blob/main/docs/index.md#_snippet_1

LANGUAGE: python
CODE:
```
from agents import Agent, Runner

agent = Agent(name="Assistant", instructions="You are a helpful assistant")

result = Runner.run_sync(agent, "Write a haiku about recursion in programming.")
print(result.final_output)
```

LANGUAGE: bash
CODE:
```
export OPENAI_API_KEY=sk-...
```

----------------------------------------

TITLE: Example: Integrate LiteLLM model with OpenAI Agent
DESCRIPTION: This Python example demonstrates how to create an `Agent` that utilizes a `LitellmModel` to interact with various AI models. It includes a custom `function_tool` for fetching weather information and handles user input for the model name and API key, showcasing a complete asynchronous agent execution flow.
SOURCE: https://github.com/openai/openai-agents-python/blob/main/docs/models/litellm.md#_snippet_1

LANGUAGE: python
CODE:
```
from __future__ import annotations

import asyncio

from agents import Agent, Runner, function_tool, set_tracing_disabled
from agents.extensions.models.litellm_model import LitellmModel

@function_tool
def get_weather(city: str):
    print(f"[debug] getting weather for {city}")
    return f"The weather in {city} is sunny."


async def main(model: str, api_key: str):
    agent = Agent(
        name="Assistant",
        instructions="You only respond in haikus.",
        model=LitellmModel(model=model, api_key=api_key),
        tools=[get_weather],
    )

    result = await Runner.run(agent, "What's the weather in Tokyo?")
    print(result.final_output)


if __name__ == "__main__":
    # First try to get model/api key from args
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--model", type=str, required=False)
    parser.add_argument("--api-key", type=str, required=False)
    args = parser.parse_args()

    model = args.model
    if not model:
        model = input("Enter a model name for Litellm: ")

    api_key = args.api_key
    if not api_key:
        api_key = input("Enter an API key for Litellm: ")

    asyncio.run(main(model, api_key))
```

----------------------------------------

TITLE: Configure Tracing and API Compatibility for OpenAI Agents
DESCRIPTION: This documentation outlines methods to resolve common issues encountered when using OpenAI Agents, specifically related to tracing and compatibility with different OpenAI API endpoints or non-OpenAI providers. It details how to manage tracing behavior and switch between OpenAI's Responses API and Chat Completions API.
SOURCE: https://github.com/openai/openai-agents-python/blob/main/docs/models/index.md#_snippet_5

LANGUAGE: APIDOC
CODE:
```
Tracing Configuration:

set_tracing_disabled(value: bool)
  - Purpose: Disables the SDK's tracing functionality.
  - Parameters:
    - value (bool): Set to `True` to disable tracing.
  - Returns: None

set_tracing_export_api_key(api_key: str)
  - Purpose: Sets a specific OpenAI API key to be used solely for uploading traces.
  - Note: This API key must originate from platform.openai.com.
  - Parameters:
    - api_key (str): The OpenAI API key string.
  - Returns: None

API Compatibility Configuration:

set_default_openai_api(api_type: str)
  - Purpose: Configures the SDK to use a specific OpenAI API endpoint by default.
  - Use Case: Recommended when `OPENAI_API_KEY` and `OPENAI_BASE_URL` are managed via environment variables.
  - Parameters:
    - api_type (str): The API type to set. Currently, 'chat_completions' is a common value to switch from the default Responses API.
  - Returns: None

OpenAIChatCompletionsModel
  - Purpose: Provides an explicit model class for interacting with OpenAI's Chat Completions API.
  - Use Case: An alternative to `set_default_openai_api` for agents that require the Chat Completions API, allowing direct instantiation of this model class for an agent's `model` parameter.
  - Example Usage (conceptual):
    OpenAIChatCompletionsModel(
        model="gpt-4o",
        openai_client=AsyncOpenAI()
    )
```

----------------------------------------

TITLE: Run MCP Streamable HTTP Example with uv
DESCRIPTION: This command demonstrates how to execute the MCP Streamable HTTP example using the `uv` tool. It initiates the Python script located at `examples/mcp/streamablehttp_example/main.py`, starting the local Streamable HTTP server.
SOURCE: https://github.com/openai/openai-agents-python/blob/main/examples/mcp/streamablehttp_example/README.md#_snippet_0

LANGUAGE: bash
CODE:
```
uv run python examples/mcp/streamablehttp_example/main.py
```

----------------------------------------

TITLE: OpenAI Agents Module Core Functions API Reference
DESCRIPTION: Documents the core functions available within the `agents` module for configuring OpenAI API access, tracing, and logging. Note that detailed parameter signatures and return types are not provided in the source text.
SOURCE: https://github.com/openai/openai-agents-python/blob/main/docs/ref/index.md#_snippet_0

LANGUAGE: APIDOC
CODE:
```
agents module functions:

  set_default_openai_key()
    - Sets the default OpenAI API key for the agents module.
    - Note: Detailed signature and parameters not provided in source.

  set_default_openai_client()
    - Sets the default OpenAI client instance to be used by the agents module.
    - Note: Detailed signature and parameters not provided in source.

  set_default_openai_api()
    - Configures the default OpenAI API base URL or other API-specific settings.
    - Note: Detailed signature and parameters not provided in source.

  set_tracing_export_api_key()
    - Configures the API key specifically for tracing data export.
    - Note: Detailed signature and parameters not provided in source.

  set_tracing_disabled()
    - Disables the tracing functionality within the agents module.
    - Note: Detailed signature and parameters not provided in source.

  set_trace_processors()
    - Allows setting custom trace processors for advanced tracing control.
    - Note: Detailed signature and parameters not provided in source.

  enable_verbose_stdout_logging()
    - Enables verbose logging output to standard output for debugging purposes.
    - Note: Detailed signature and parameters not provided in source.
```

----------------------------------------

TITLE: MCP Server Tool Interface and Agent Interaction
DESCRIPTION: This documentation describes the interface of tools exposed by the MCP filesystem server and how a Python agent interacts with them. It covers the process of tool discovery and execution for file system operations.
SOURCE: https://github.com/openai/openai-agents-python/blob/main/examples/mcp/filesystem_example/README.md#_snippet_2

LANGUAGE: APIDOC
CODE:
```
MCPServer Tool Interface:

list_directory(path: str = '.'):
  - Description: Lists the contents of a directory accessible by the MCP server.
  - Parameters:
    - path: The directory path to list. Defaults to the current working directory if not specified.
  - Returns: A list of strings, where each string is a file or directory name.

read_file(file_path: str):
  - Description: Reads the entire content of a specified file from the MCP server's accessible file system.
  - Parameters:
    - file_path: The full path to the file to be read.
  - Returns: The content of the file as a string.

list_tools():
  - Description: Fetches the list of available tools exposed by the MCP server. This method is called by the agent to dynamically discover capabilities.
  - Parameters: None
  - Returns: A list of tool definitions, typically including tool names, descriptions, and expected parameters.

run_tool(tool_name: str, *args, **kwargs):
  - Description: Executes a specified tool on the MCP server. This is the primary method for the agent to invoke server-side functionality.
  - Parameters:
    - tool_name: The name of the tool to execute (e.g., 'list_directory', 'read_file').
    - *args, **kwargs: Variable arguments and keyword arguments passed to the specific tool being executed, as required by its signature.
  - Returns: The result of the tool execution, which varies based on the tool's purpose.
  - Usage Notes: The agent first calls `list_tools()` to identify available tools and their signatures before invoking `run_tool()`.
```

----------------------------------------

TITLE: MCP Prompt Server Interface
DESCRIPTION: Describes the interface for interacting with the local MCP prompt server, including the `MCPServerStreamableHttp` class and the `generate_code_review_instructions` prompt. This interface allows agents to dynamically fetch instructions based on user-defined parameters.
SOURCE: https://github.com/openai/openai-agents-python/blob/main/examples/mcp/prompt_server/README.md#_snippet_1

LANGUAGE: APIDOC
CODE:
```
Class: MCPServerStreamableHttp
  Module: agents.mcp
  Description: Handles streaming HTTP responses for MCP prompts, enabling dynamic instruction generation for agents.

Prompt: generate_code_review_instructions
  Description: Generates agent instructions specifically tailored for code review tasks.
  Parameters:
    - focus (string): Specifies the area of code review (e.g., "security vulnerabilities", "performance").
    - language (string): Indicates the programming language of the code to be reviewed (e.g., "python", "java").
  Returns: string (Dynamically generated agent instructions based on the provided focus and language.)
```

----------------------------------------

TITLE: Execute Custom LLM Provider Example Script
DESCRIPTION: This command demonstrates how to run a specific Python example script that utilizes a custom LLM provider. It assumes the necessary environment variables (base URL, API key, and model name) have already been configured as shown in the previous step, allowing the script to connect to the specified custom LLM service.
SOURCE: https://github.com/openai/openai-agents-python/blob/main/examples/model_providers/README.md#_snippet_1

LANGUAGE: python
CODE:
```
python examples/model_providers/custom_example_provider.py
```

----------------------------------------

TITLE: Basic Agent Creation and Synchronous Run
DESCRIPTION: This example demonstrates how to create a simple `Agent` with instructions and run it synchronously using `Runner.run_sync()`. It showcases the fundamental setup for an agent to process a prompt and print its final output, requiring the `OPENAI_API_KEY` environment variable.
SOURCE: https://github.com/openai/openai-agents-python/blob/main/README.md#_snippet_3

LANGUAGE: python
CODE:
```
from agents import Agent, Runner

agent = Agent(name="Assistant", instructions="You are a helpful assistant")

result = Runner.run_sync(agent, "Write a haiku about recursion in programming.")
print(result.final_output)

# Code within the code,
# Functions calling themselves,
# Infinite loop's dance.
```

----------------------------------------

TITLE: Customize OpenAI API Type for SDK
DESCRIPTION: Illustrates how to override the default OpenAI Responses API to use the Chat Completions API by calling `set_default_openai_api()`.
SOURCE: https://github.com/openai/openai-agents-python/blob/main/docs/config.md#_snippet_2

LANGUAGE: python
CODE:
```
from agents import set_default_openai_api

set_default_openai_api("chat_completions")
```

----------------------------------------

TITLE: MCP Server Classes and Tool Management API
DESCRIPTION: Documentation for the core classes used to interact with Model Context Protocol (MCP) servers within the Agents SDK, including methods for tool listing, calling, and caching mechanisms.
SOURCE: https://github.com/openai/openai-agents-python/blob/main/docs/ja/mcp.md#_snippet_2

LANGUAGE: APIDOC
CODE:
```
MCPServerStdio(params: dict)
MCPServerSse(url: str)
MCPServerStreamableHttp(url: str)
  - Base classes for connecting to different types of MCP servers.
  - Parameters:
    - params (dict): Configuration for stdio server (e.g., command, args).
    - url (str): URL for SSE or Streamable HTTP servers.

MCPServer.constructor(..., cache_tools_list: bool = False)
  - cache_tools_list (bool): If True, enables caching of the tool list retrieved from the MCP server.
                             Use only when the tool list is static.

MCPServer.list_tools(run_context: RunContextWrapper, agent: Agent) -> List[Tool]
  - Retrieves the list of tools provided by the MCP server.
  - Called automatically by the Agents SDK during agent execution.
  - Can be called directly for inspection, requiring run_context and agent parameters.

MCPServer.call_tool(tool_name: str, *args, **kwargs) -> Any
  - Executes a specific tool provided by the MCP server.
  - Called automatically by the Agents SDK when the LLM invokes an MCP server tool.

MCPServer.invalidate_tools_cache()
  - Invalidates the cached tool list for the server, forcing a fresh retrieval on the next list_tools() call.
```

----------------------------------------

TITLE: Example User Query for Financial Research Agent
DESCRIPTION: Illustrates a typical natural language query that an end-user might provide to the financial research agent. This query serves as the input for the agent's analysis and report generation process.
SOURCE: https://github.com/openai/openai-agents-python/blob/main/examples/financial_research_agent/README.md#_snippet_1

LANGUAGE: text
CODE:
```
Write up an analysis of Apple Inc.'s most recent quarter.
```

----------------------------------------

TITLE: Initialize Agent with Web Search and File Search Tools
DESCRIPTION: This Python example demonstrates how to create an Agent instance and equip it with both `WebSearchTool` for general web queries and `FileSearchTool` for retrieving information from specified OpenAI Vector Stores. It shows how to configure `FileSearchTool` with parameters like `max_num_results` and `vector_store_ids`, and then run a query asynchronously using the `Runner`.
SOURCE: https://github.com/openai/openai-agents-python/blob/main/docs/tools.md#_snippet_0

LANGUAGE: python
CODE:
```
from agents import Agent, FileSearchTool, Runner, WebSearchTool

agent = Agent(
    name="Assistant",
    tools=[
        WebSearchTool(),
        FileSearchTool(
            max_num_results=3,
            vector_store_ids=["VECTOR_STORE_ID"]
        )
    ]
)

async def main():
    result = await Runner.run(agent, "Which coffee shop should I go to, taking into account my preferences and the weather today in SF?")
    print(result.final_output)
```

----------------------------------------

TITLE: MCP Server Prompt Management API
DESCRIPTION: Defines the methods available on MCP servers for listing and retrieving prompts, including their parameters, return types, and usage for dynamic agent instruction generation.
SOURCE: https://github.com/openai/openai-agents-python/blob/main/docs/mcp.md#_snippet_6

LANGUAGE: APIDOC
CODE:
```
list_prompts()
  - Lists all available prompts on the server.
  - Returns: A result object containing a 'prompts' list, where each item has 'name' and 'description'.

get_prompt(name: str, arguments: dict)
  - Retrieves a specific prompt by name, allowing for dynamic customization via arguments.
  - Parameters:
    - name (str): The name of the prompt to retrieve.
    - arguments (dict): A dictionary of key-value pairs to customize the prompt's output.
  - Returns: A result object containing 'messages', typically 'messages[0].content.text' holds the generated instructions.
```

----------------------------------------

TITLE: Start Local MCP Filesystem Server with npx
DESCRIPTION: This command launches the Model Context Protocol (MCP) filesystem server locally using `npx`. The `-y` flag automatically confirms prompts, and `<samples_directory>` specifies the directory the server will expose, enabling file operations for the agent.
SOURCE: https://github.com/openai/openai-agents-python/blob/main/examples/mcp/filesystem_example/README.md#_snippet_1

LANGUAGE: Bash
CODE:
```
npx -y "@modelcontextprotocol/server-filesystem" <samples_directory>
```

----------------------------------------

TITLE: Run Financial Research Agent Example
DESCRIPTION: Provides the command-line instruction to execute the financial research agent application. This command initiates the agent's workflow, allowing it to process user queries and generate reports.
SOURCE: https://github.com/openai/openai-agents-python/blob/main/examples/financial_research_agent/README.md#_snippet_0

LANGUAGE: bash
CODE:
```
python -m examples.financial_research_agent.main
```

----------------------------------------

TITLE: Configure a Basic Agent with Instructions and Tools
DESCRIPTION: Demonstrates how to initialize an `Agent` with a name, instructions, model, and a function tool. The `get_weather` function is defined as an example tool using the `@function_tool` decorator, showcasing how agents can interact with external capabilities.
SOURCE: https://github.com/openai/openai-agents-python/blob/main/docs/agents.md#_snippet_0

LANGUAGE: Python
CODE:
```
from agents import Agent, ModelSettings, function_tool

@function_tool
def get_weather(city: str) -> str:
    return f"The weather in {city} is sunny"

agent = Agent(
    name="Haiku agent",
    instructions="Always respond in haiku form",
    model="o3-mini",
    tools=[get_weather],
)
```

----------------------------------------

TITLE: Configure Tracing Export API Key
DESCRIPTION: Explains how to specifically set the API key used for tracing exports, separate from the main LLM API key, using `set_tracing_export_api_key()`.
SOURCE: https://github.com/openai/openai-agents-python/blob/main/docs/config.md#_snippet_3

LANGUAGE: python
CODE:
```
from agents import set_tracing_export_api_key

set_tracing_export_api_key("sk-...")
```

----------------------------------------

TITLE: Senior Writer Agent Initial Prompt
DESCRIPTION: Defines the initial instructions and context provided to the senior writer agent. This prompt guides the agent on its role, how to synthesize information from search summaries and sub-analyst tools, and the expected structure of the final markdown report, including follow-up questions.
SOURCE: https://github.com/openai/openai-agents-python/blob/main/examples/financial_research_agent/README.md#_snippet_2

LANGUAGE: text
CODE:
```
You are a senior financial analyst. You will be provided with the original query\nand a set of raw search summaries. Your job is to synthesize these into a\nlong‑form markdown report (at least several paragraphs) with a short executive\nsummary. You also have access to tools like `fundamentals_analysis` and\n`risk_analysis` to get short specialist write‑ups if you want to incorporate them.\nAdd a few follow‑up questions for further research.
```

----------------------------------------

TITLE: Start Local MCP Git Server
DESCRIPTION: This command starts the local Git MCP server using `uvx`, which exposes various Git-related tools to the agent. This server runs as a subprocess and facilitates communication between the agent and Git operations.
SOURCE: https://github.com/openai/openai-agents-python/blob/main/examples/mcp/git_example/README.md#_snippet_1

LANGUAGE: bash
CODE:
```
uvx mcp-server-git
```

----------------------------------------

TITLE: Execute OpenAI Research Bot for Product Recommendations
DESCRIPTION: This command-line snippet demonstrates how to run the OpenAI research bot's main script using `uv`. It initiates a research process to generate a detailed report, in this case, on surfboard recommendations for beginners. The output includes progress indicators and a summary of the generated report.
SOURCE: https://github.com/openai/openai-agents-python/blob/main/examples/research_bot/sample_outputs/product_recs.txt#_snippet_0

LANGUAGE: bash
CODE:
```
$ uv run python -m examples.research_bot.main
```

----------------------------------------

TITLE: Create Custom Function Tools Manually
DESCRIPTION: This example illustrates how to manually create a `FunctionTool` instance when automatic inference from Python functions is not desired. It requires explicitly providing the tool's name, description, a Pydantic `BaseModel` for the input JSON schema, and an `on_invoke_tool` async function to handle tool execution and argument parsing.
SOURCE: https://github.com/openai/openai-agents-python/blob/main/docs/tools.md#_snippet_2

LANGUAGE: python
CODE:
```
from typing import Any

from pydantic import BaseModel

from agents import RunContextWrapper, FunctionTool



def do_some_work(data: str) -> str:
    return "done"


class FunctionArgs(BaseModel):
    username: str
    age: int


async def run_function(ctx: RunContextWrapper[Any], args: str) -> str:
    parsed = FunctionArgs.model_validate_json(args)
    return do_some_work(data=f"{parsed.username} is {parsed.age} years old")


tool = FunctionTool(
    name="process_user",
    description="Processes extracted user data",
    params_json_schema=FunctionArgs.model_json_schema(),
    on_invoke_tool=run_function,
)
```

----------------------------------------

TITLE: Run MCP Filesystem Example with uv
DESCRIPTION: This command executes the main Python script for the MCP filesystem example using the `uv` tool. It initiates the application demonstrating the integration of Python agents with the MCP server for file system operations.
SOURCE: https://github.com/openai/openai-agents-python/blob/main/examples/mcp/filesystem_example/README.md#_snippet_0

LANGUAGE: Bash
CODE:
```
uv run python examples/mcp/filesystem_example/main.py
```

----------------------------------------

TITLE: Running an OpenAI Agent Asynchronously
DESCRIPTION: This snippet demonstrates how to initialize an `Agent` with specific instructions and then execute it asynchronously using `Runner.run()`. The example prompts the agent to write a haiku about recursion and prints the final generated output.
SOURCE: https://github.com/openai/openai-agents-python/blob/main/docs/running_agents.md#_snippet_0

LANGUAGE: python
CODE:
```
from agents import Agent, Runner

async def main():
    agent = Agent(name="Assistant", instructions="You are a helpful assistant")

    result = await Runner.run(agent, "Write a haiku about recursion in programming.")
    print(result.final_output)
    # Code within the code,
    # Functions calling themselves,
    # Infinite loop's dance.
```

----------------------------------------

TITLE: Run MCP Git Example Python Script
DESCRIPTION: This command executes the main Python script for the MCP Git example using `uv` to manage the environment. It initiates the agent that interacts with the local Git MCP server, demonstrating the agent's capabilities.
SOURCE: https://github.com/openai/openai-agents-python/blob/main/examples/mcp/git_example/README.md#_snippet_0

LANGUAGE: bash
CODE:
```
uv run python examples/mcp/git_example/main.py
```

----------------------------------------

TITLE: MCP Server Tool List Caching API
DESCRIPTION: Describes how to enable and manage caching for the MCP server's tool list to improve performance. It covers the `cache_tools_list` constructor parameter and the `invalidate_tools_cache` method.
SOURCE: https://github.com/openai/openai-agents-python/blob/main/docs/mcp.md#_snippet_7

LANGUAGE: APIDOC
CODE:
```
MCPServerStdio(cache_tools_list: bool = False, ...)
MCPServerSse(cache_tools_list: bool = False, ...)
MCPServerStreamableHttp(cache_tools_list: bool = False, ...)
  - Constructor parameter to enable automatic caching of the tool list.
  - Parameters:
    - cache_tools_list (bool): If True, the list of tools will be cached. Should only be used if the tool list is static.

invalidate_tools_cache()
  - Invalidates the cached tool list on the server instance.
  - Call this method when the underlying tool list is known to have changed to ensure fresh data.
```

----------------------------------------

TITLE: Build Project Documentation and Generate Coverage with Make
DESCRIPTION: The `make build-docs` command compiles the project's documentation, which is useful for verifying changes to markdown pages or the `mkdocs.yml` configuration. Additionally, `make coverage` can be used to generate a test coverage report.
SOURCE: https://github.com/openai/openai-agents-python/blob/main/AGENTS.md#_snippet_2

LANGUAGE: bash
CODE:
```
make build-docs
```

LANGUAGE: bash
CODE:
```
make coverage
```

----------------------------------------

TITLE: Configure OpenAI API Key for SDK
DESCRIPTION: Demonstrates how to programmatically set the default OpenAI API key using `set_default_openai_key()` if the `OPENAI_API_KEY` environment variable is not set before the SDK is imported.
SOURCE: https://github.com/openai/openai-agents-python/blob/main/docs/config.md#_snippet_0

LANGUAGE: python
CODE:
```
from agents import set_default_openai_key

set_default_openai_key("sk-...")
```

----------------------------------------

TITLE: Stream LLM Text Token-by-Token with OpenAI Agents
DESCRIPTION: This Python example demonstrates how to stream raw LLM response events using `Runner.run_streamed()` to display text generated by the LLM token-by-token. It filters for `raw_response_event` and extracts `ResponseTextDeltaEvent` data to print the `delta` content.
SOURCE: https://github.com/openai/openai-agents-python/blob/main/docs/streaming.md#_snippet_0

LANGUAGE: python
CODE:
```
import asyncio
from openai.types.responses import ResponseTextDeltaEvent
from agents import Agent, Runner

async def main():
    agent = Agent(
        name="Joker",
        instructions="You are a helpful assistant.",
    )

    result = Runner.run_streamed(agent, input="Please tell me 5 jokes.")
    async for event in result.stream_events():
        if event.type == "raw_response_event" and isinstance(event.data, ResponseTextDeltaEvent):
            print(event.data.delta, end="", flush=True)


if __name__ == "__main__":
    asyncio.run(main())
```

----------------------------------------

TITLE: Complete Agent Orchestration Workflow with Handoffs and Input Guardrails
DESCRIPTION: This comprehensive example integrates agent definitions, handoffs, and an input guardrail into a full asynchronous workflow. It demonstrates how a `Triage Agent` can route queries to specialist agents while enforcing custom validation rules before processing, showcasing a robust multi-agent system.
SOURCE: https://github.com/openai/openai-agents-python/blob/main/docs/quickstart.md#_snippet_9

LANGUAGE: python
CODE:
```
from agents import Agent, InputGuardrail, GuardrailFunctionOutput, Runner
from pydantic import BaseModel
import asyncio

class HomeworkOutput(BaseModel):
    is_homework: bool
    reasoning: str

guardrail_agent = Agent(
    name="Guardrail check",
    instructions="Check if the user is asking about homework.",
    output_type=HomeworkOutput,
)

math_tutor_agent = Agent(
    name="Math Tutor",
    handoff_description="Specialist agent for math questions",
    instructions="You provide help with math problems. Explain your reasoning at each step and include examples",
)

history_tutor_agent = Agent(
    name="History Tutor",
    handoff_description="Specialist agent for historical questions",
    instructions="You provide assistance with historical queries. Explain important events and context clearly.",
)


async def homework_guardrail(ctx, agent, input_data):
    result = await Runner.run(guardrail_agent, input_data, context=ctx.context)
    final_output = result.final_output_as(HomeworkOutput)
    return GuardrailFunctionOutput(
        output_info=final_output,
        tripwire_triggered=not final_output.is_homework,
    )

triage_agent = Agent(
    name="Triage Agent",
    instructions="You determine which agent to use based on the user's homework question",
    handoffs=[history_tutor_agent, math_tutor_agent],
    input_guardrails=[
        InputGuardrail(guardrail_function=homework_guardrail),
    ],
)

async def main():
    result = await Runner.run(triage_agent, "who was the first president of the united states?")
    print(result.final_output)

    result = await Runner.run(triage_agent, "what is life")
    print(result.final_output)

if __name__ == "__main__":
    asyncio.run(main())
```

----------------------------------------

TITLE: Customize Python Logging for SDK
DESCRIPTION: Provides an example of how to customize the SDK's Python loggers (`openai.agents` or `openai.agents.tracing`) by setting log levels and adding handlers for fine-grained control over log output.
SOURCE: https://github.com/openai/openai-agents-python/blob/main/docs/config.md#_snippet_6

LANGUAGE: python
CODE:
```
import logging

logger = logging.getLogger("openai.agents") # or openai.agents.tracing for the Tracing logger

# To make all logs show up
logger.setLevel(logging.DEBUG)
# To make info and above show up
logger.setLevel(logging.INFO)
# To make warning and above show up
logger.setLevel(logging.WARNING)
# etc

# You can customize this as needed, but this will output to `stderr` by default
logger.addHandler(logging.StreamHandler())
```

----------------------------------------

TITLE: Initialize Agent with LiteLLM Non-OpenAI Models
DESCRIPTION: This Python code demonstrates how to initialize an `Agent` instance using models provided through the LiteLLM integration. By prefixing the model name with `litellm/`, you can specify models from various providers like Anthropic's Claude or Google's Gemini, leveraging LiteLLM's unified API.
SOURCE: https://github.com/openai/openai-agents-python/blob/main/docs/models/index.md#_snippet_1

LANGUAGE: python
CODE:
```
claude_agent = Agent(model="litellm/anthropic/claude-3-5-sonnet-20240620", ...)
gemini_agent = Agent(model="litellm/gemini/gemini-2.5-flash-preview-04-17", ...)
```

----------------------------------------

TITLE: Run MCP SSE Example Application
DESCRIPTION: This command executes the MCP SSE example application. It uses the `uv` tool to run the main Python script located in the `examples/mcp/sse_example/` directory.
SOURCE: https://github.com/openai/openai-agents-python/blob/main/examples/mcp/sse_example/README.md#_snippet_0

LANGUAGE: bash
CODE:
```
uv run python examples/mcp/sse_example/main.py
```

----------------------------------------

TITLE: Define Function Tools Automatically with Python Decorators
DESCRIPTION: This snippet demonstrates how to define function tools using the `@function_tool` decorator from the `agents` SDK. It showcases automatic inference of tool names, descriptions from docstrings, and input schemas from type hints, including `TypedDict` for complex arguments. The example also shows how to inspect the generated tool properties like name, description, and JSON schema.
SOURCE: https://github.com/openai/openai-agents-python/blob/main/docs/tools.md#_snippet_1

LANGUAGE: python
CODE:
```
import json

from typing_extensions import TypedDict, Any

from agents import Agent, FunctionTool, RunContextWrapper, function_tool


class Location(TypedDict):
    lat: float
    long: float

@function_tool  # (1)!
async def fetch_weather(location: Location) -> str:
    # (2)!
    """Fetch the weather for a given location.

    Args:
        location: The location to fetch the weather for.
    """
    # In real life, we'd fetch the weather from a weather API
    return "sunny"


@function_tool(name_override="fetch_data")  # (3)!
def read_file(ctx: RunContextWrapper[Any], path: str, directory: str | None = None) -> str:
    """Read the contents of a file.

    Args:
        path: The path to the file to read.
        directory: The directory to read the file from.
    """
    # In real life, we'd read the file from the file system
    return "<file contents>"


agent = Agent(
    name="Assistant",
    tools=[fetch_weather, read_file],  # (4)!
)

for tool in agent.tools:
    if isinstance(tool, FunctionTool):
        print(tool.name)
        print(tool.description)
        print(json.dumps(tool.params_json_schema, indent=2))
        print()
```

LANGUAGE: json
CODE:
```
{
"$defs": {
  "Location": {
    "properties": {
      "lat": {
        "title": "Lat",
        "type": "number"
      },
      "long": {
        "title": "Long",
        "type": "number"
      }
    },
    "required": [
      "lat",
      "long"
    ],
    "title": "Location",
    "type": "object"
  }
},
"properties": {
  "location": {
    "$ref": "#/$defs/Location",
    "description": "The location to fetch the weather for."
  }
},
"required": [
  "location"
],
"title": "fetch_weather_args",
"type": "object"
}

fetch_data
Read the contents of a file.
{
"properties": {
  "path": {
    "description": "The path to the file to read.",
    "title": "Path",
    "type": "string"
  },
  "directory": {
    "anyOf": [
      {
        "type": "string"
      },
      {
        "type": "null"
      }
    ],
    "default": null,
    "description": "The directory to read the file from.",
    "title": "Directory"
  }
},
"required": [
  "path"
],
"title": "fetch_data_args",
"type": "object"
}
```

----------------------------------------

TITLE: Configure Environment Variables for Custom LLM Provider
DESCRIPTION: This snippet shows how to set essential environment variables (base URL, API key, and model name) required for connecting to and using a custom Large Language Model (LLM) provider. These variables must be exported in your shell environment before running any examples that interact with the custom provider.
SOURCE: https://github.com/openai/openai-agents-python/blob/main/examples/model_providers/README.md#_snippet_0

LANGUAGE: bash
CODE:
```
export EXAMPLE_BASE_URL="..."
export EXAMPLE_API_KEY="..."
export EXAMPLE_MODEL_NAME"..."
```

----------------------------------------

TITLE: Run MCP Prompt Server Example
DESCRIPTION: This command executes the main script for the MCP prompt server example using `uv run`, which is a common way to run Python applications with dependency management. The server will run in a sub-process, typically at `http://localhost:8000/mcp`.
SOURCE: https://github.com/openai/openai-agents-python/blob/main/examples/mcp/prompt_server/README.md#_snippet_0

LANGUAGE: bash
CODE:
```
uv run python examples/mcp/prompt_server/main.py
```

----------------------------------------

TITLE: Run Agent with Custom Configurations as a Tool in Python
DESCRIPTION: This example illustrates how to create a custom function tool that directly invokes `Runner.run` with advanced configurations like `max_turns`. This approach is necessary when `agent.as_tool()` does not provide sufficient flexibility for specific agent execution parameters, allowing for fine-grained control over the sub-agent's behavior.
SOURCE: https://github.com/openai/openai-agents-python/blob/main/docs/tools.md#_snippet_4

LANGUAGE: python
CODE:
```
@function_tool
async def run_my_agent() -> str:
    """A tool that runs the agent with custom configs"""

    agent = Agent(name="My agent", instructions="...")

    result = await Runner.run(
        agent,
        input="...",
        max_turns=5,
        run_config=...
    )

    return str(result.final_output)
```

----------------------------------------

TITLE: Define a Single OpenAI Agent
DESCRIPTION: This Python snippet demonstrates how to instantiate a basic `Agent` object from the `agents` SDK. An agent is defined by its `name` and `instructions`, which guide its behavior and purpose within an AI system.
SOURCE: https://github.com/openai/openai-agents-python/blob/main/docs/quickstart.md#_snippet_4

LANGUAGE: python
CODE:
```
from agents import Agent

agent = Agent(
    name="Math Tutor",
    instructions="You provide help with math problems. Explain your reasoning at each step and include examples",
)
```

----------------------------------------

TITLE: Manage Multi-Turn Conversations with OpenAI Agents
DESCRIPTION: This asynchronous Python example demonstrates how to conduct multi-turn conversations using the `Runner.run` method. It shows how to capture the `RunResultBase.to_input_list()` for subsequent turns, allowing agents to maintain context across user interactions and respond to follow-up questions.
SOURCE: https://github.com/openai/openai-agents-python/blob/main/docs/running_agents.md#_snippet_2

LANGUAGE: python
CODE:
```
async def main():
    agent = Agent(name="Assistant", instructions="Reply very concisely.")

    with trace(workflow_name="Conversation", group_id=thread_id):
        # First turn
        result = await Runner.run(agent, "What city is the Golden Gate Bridge in?")
        print(result.final_output)
        # San Francisco

        # Second turn
        new_input = result.to_input_list() + [{"role": "user", "content": "What state is it in?"}]
        result = await Runner.run(agent, new_input)
        print(result.final_output)
        # California
```

----------------------------------------

TITLE: Set OpenAI API Key Environment Variable
DESCRIPTION: This command sets the OpenAI API key as an environment variable. This key is required for authenticating requests to the OpenAI API and should be kept confidential and never hardcoded directly in source files.
SOURCE: https://github.com/openai/openai-agents-python/blob/main/docs/quickstart.md#_snippet_3

LANGUAGE: bash
CODE:
```
export OPENAI_API_KEY=sk-...
```

----------------------------------------

TITLE: Install OpenAI Agents SDK
DESCRIPTION: This command installs the core OpenAI Agents SDK using pip, Python's package installer. It fetches the necessary libraries to start building multi-agent applications. An optional `voice` group can be installed for voice support.
SOURCE: https://github.com/openai/openai-agents-python/blob/main/README.md#_snippet_2

LANGUAGE: bash
CODE:
```
pip install openai-agents
```

----------------------------------------

TITLE: Run Code Formatting, Linting, and Type Checking with Make
DESCRIPTION: These `make` commands automate code quality checks. `make format` applies consistent code styling, `make lint` identifies potential errors and stylistic issues, and `make mypy` performs static type checking to ensure type correctness in Python code.
SOURCE: https://github.com/openai/openai-agents-python/blob/main/AGENTS.md#_snippet_0

LANGUAGE: bash
CODE:
```
make format
make lint
make mypy
```

----------------------------------------

TITLE: Implement Input Guardrail for Agent
DESCRIPTION: Demonstrates how to create and integrate an input guardrail using an auxiliary agent to check user input before processing. It shows the setup of the guardrail function, its integration into the main agent, and an example of triggering the guardrail when specific input conditions are met.
SOURCE: https://github.com/openai/openai-agents-python/blob/main/docs/guardrails.md#_snippet_0

LANGUAGE: python
CODE:
```
from pydantic import BaseModel
from agents import (
    Agent,
    GuardrailFunctionOutput,
    InputGuardrailTripwireTriggered,
    RunContextWrapper,
    Runner,
    TResponseInputItem,
    input_guardrail,
)

class MathHomeworkOutput(BaseModel):
    is_math_homework: bool
    reasoning: str

guardrail_agent = Agent( # (1)!
    name="Guardrail check",
    instructions="Check if the user is asking you to do their math homework.",
    output_type=MathHomeworkOutput,
)


@input_guardrail
async def math_guardrail( # (2)!
    ctx: RunContextWrapper[None], agent: Agent, input: str | list[TResponseInputItem]
) -> GuardrailFunctionOutput:
    result = await Runner.run(guardrail_agent, input, context=ctx.context)

    return GuardrailFunctionOutput(
        output_info=result.final_output, # (3)!
        tripwire_triggered=result.final_output.is_math_homework,
    )


agent = Agent(  # (4)!
    name="Customer support agent",
    instructions="You are a customer support agent. You help customers with their questions.",
    input_guardrails=[math_guardrail],
)

async def main():
    # This should trip the guardrail
    try:
        await Runner.run(agent, "Hello, can you help me solve for x: 2x + 3 = 11?")
        print("Guardrail didn't trip - this is unexpected")

    except InputGuardrailTripwireTriggered:
        print("Math homework guardrail tripped")
```

----------------------------------------

TITLE: Stream High-Level Agent and Run Item Events
DESCRIPTION: This Python example illustrates how to process higher-level stream events like `RunItemStreamEvent` and `AgentUpdatedStreamEvent` to provide progress updates at a coarser granularity than token-by-token. It shows how to define a `function_tool`, ignore raw events, and print updates when an agent changes or when tool calls, tool outputs, or message outputs occur.
SOURCE: https://github.com/openai/openai-agents-python/blob/main/docs/streaming.md#_snippet_1

LANGUAGE: python
CODE:
```
import asyncio
import random
from agents import Agent, ItemHelpers, Runner, function_tool

@function_tool
def how_many_jokes() -> int:
    return random.randint(1, 10)


async def main():
    agent = Agent(
        name="Joker",
        instructions="First call the `how_many_jokes` tool, then tell that many jokes.",
        tools=[how_many_jokes],
    )

    result = Runner.run_streamed(
        agent,
        input="Hello",
    )
    print("=== Run starting ===")

    async for event in result.stream_events():
        # We'll ignore the raw responses event deltas
        if event.type == "raw_response_event":
            continue
        # When the agent updates, print that
        elif event.type == "agent_updated_stream_event":
            print(f"Agent updated: {event.new_agent.name}")
            continue
        # When items are generated, print them
        elif event.type == "run_item_stream_event":
            if event.item.type == "tool_call_item":
                print("-- Tool was called")
            elif event.item.type == "tool_call_output_item":
                print(f"-- Tool output: {event.item.output}")
            elif event.item.type == "message_output_item":
                print(f"-- Message output:\n {ItemHelpers.text_message_output(event.item)}")
            else:
                pass  # Ignore other event types

    print("=== Run complete ===")


if __name__ == "__main__":
    asyncio.run(main())
```

----------------------------------------

TITLE: Grouping Multiple Agent Runs into a Single Trace in Python
DESCRIPTION: This Python example demonstrates how to use the `trace()` context manager to encapsulate multiple `Runner.run()` calls within a single, overarching trace. This approach is useful for consolidating the tracing data of a complex workflow that involves several distinct agent interactions into a unified view.
SOURCE: https://github.com/openai/openai-agents-python/blob/main/docs/tracing.md#_snippet_1

LANGUAGE: Python
CODE:
```
from agents import Agent, Runner, trace

async def main():
    agent = Agent(name="Joke generator", instructions="Tell funny jokes.")

    with trace("Joke workflow"):
        first_result = await Runner.run(agent, "Tell me a joke")
        second_result = await Runner.run(agent, f"Rate this joke: {first_result.final_output}")
        print(f"Joke: {first_result.final_output}")
        print(f"Rating: {second_result.final_output}")
```

----------------------------------------

TITLE: Configure Agents with Different OpenAI Models in Python
DESCRIPTION: This Python example demonstrates how to initialize `Agent` instances with various OpenAI models. It showcases configuring an agent by directly providing a model name string and another by instantiating an `OpenAIChatCompletionsModel` object, enabling flexible model selection within a multi-agent workflow. A `triage_agent` is also shown orchestrating handoffs based on language.
SOURCE: https://github.com/openai/openai-agents-python/blob/main/docs/models/index.md#_snippet_2

LANGUAGE: Python
CODE:
```
from agents import Agent, Runner, AsyncOpenAI, OpenAIChatCompletionsModel
import asyncio

spanish_agent = Agent(
    name="Spanish agent",
    instructions="You only speak Spanish.",
    model="o3-mini" # (1)!
)

english_agent = Agent(
    name="English agent",
    instructions="You only speak English",
    model=OpenAIChatCompletionsModel( # (2)!
        model="gpt-4o",
        openai_client=AsyncOpenAI()
    )
)

triage_agent = Agent(
    name="Triage agent",
    instructions="Handoff to the appropriate agent based on the language of the request.",
    handoffs=[spanish_agent, english_agent],
    model="gpt-3.5-turbo",
)

async def main():
    result = await Runner.run(triage_agent, input="Hola, ¿cómo estás?")
    print(result.final_output)
```

----------------------------------------

TITLE: Managing Local Context with RunContextWrapper in Python Agents
DESCRIPTION: This Python example demonstrates how to pass and access local context within an agent's tools and run methods using `RunContextWrapper`. It shows defining a dataclass for context, passing it to the `Runner.run` function, and accessing it from within a `function_tool`, ensuring type safety and illustrating that this context is not sent to the LLM.
SOURCE: https://github.com/openai/openai-agents-python/blob/main/docs/context.md#_snippet_0

LANGUAGE: python
CODE:
```
import asyncio
from dataclasses import dataclass

from agents import Agent, RunContextWrapper, Runner, function_tool

@dataclass
class UserInfo:
    name: str
    uid: int

@function_tool
async def fetch_user_age(wrapper: RunContextWrapper[UserInfo]) -> str:
    """Fetch the age of the user. Call this function to get user's age information."""
    return f"The user {wrapper.context.name} is 47 years old"

async def main():
    user_info = UserInfo(name="John", uid=123)

    agent = Agent[UserInfo](
        name="Assistant",
        tools=[fetch_user_age]
    )

    result = await Runner.run(
        starting_agent=agent,
        input="What is the age of the user?",
        context=user_info
    )

    print(result.final_output)

if __name__ == "__main__":
    asyncio.run(main())
```

----------------------------------------

TITLE: Agent Handoffs for Language-Based Routing
DESCRIPTION: This example illustrates the concept of agent handoffs, where a `Triage agent` routes requests to specialized agents (Spanish or English) based on the input language. It showcases how to define agents with specific instructions and configure handoffs for dynamic workflow management using asynchronous execution.
SOURCE: https://github.com/openai/openai-agents-python/blob/main/README.md#_snippet_4

LANGUAGE: python
CODE:
```
from agents import Agent, Runner
import asyncio

spanish_agent = Agent(
    name="Spanish agent",
    instructions="You only speak Spanish.",
)

english_agent = Agent(
    name="English agent",
    instructions="You only speak English",
)

triage_agent = Agent(
    name="Triage agent",
    instructions="Handoff to the appropriate agent based on the language of the request.",
    handoffs=[spanish_agent, english_agent],
)


async def main():
    result = await Runner.run(triage_agent, input="Hola, ¿cómo estás?")
    print(result.final_output)
    # ¡Hola! Estoy bien, gracias por preguntar. ¿Y tú, cómo estás?


if __name__ == "__main__":
    asyncio.run(main())
```

----------------------------------------

TITLE: Agents SDK Handoff Function and Configuration API Reference
DESCRIPTION: Comprehensive documentation for the `handoff` function and related parameters used to configure agent handoffs. This includes details on customizing handoff behavior, defining input types, applying input filters for conversation history, and integrating recommended prompt instructions for LLMs.
SOURCE: https://github.com/openai/openai-agents-python/blob/main/docs/ja/handoffs.md#_snippet_5

LANGUAGE: APIDOC
CODE:
```
agents.handoffs.handoff(
  agent: Agent,
  tool_name_override: Optional[str] = None,
  tool_description_override: Optional[str] = None,
  on_handoff: Optional[Callable] = None,
  input_type: Optional[Type[BaseModel]] = None,
  input_filter: Optional[Callable[[HandoffInputData], HandoffInputData]] = None
)
  - Configures a handoff to another agent with customizable behavior.
  - Parameters:
    - agent (Agent): The target agent to hand off to.
    - tool_name_override (str, optional): Overrides the default tool name (transfer_to_<agent_name>).
    - tool_description_override (str, optional): Overrides the default tool description.
    - on_handoff (Callable, optional): A callback function executed when the handoff is triggered. Receives RunContextWrapper and optionally input_data.
    - input_type (Type[BaseModel], optional): A Pydantic BaseModel defining the expected input data structure for the handoff.
    - input_filter (Callable[[HandoffInputData], HandoffInputData], optional): A function to filter or modify the input data (conversation history) passed to the next agent.
  - Returns: A configured Handoff object.

agents.agent.Agent.handoffs: List[Union[Agent, Handoff]]
  - Parameter of the Agent class to specify agents or Handoff objects for delegation.

agents.handoffs.HandoffInputData
  - Data structure representing the input passed during a handoff, typically containing conversation history.

agents.extensions.handoff_filters.remove_all_tools(data: HandoffInputData) -> HandoffInputData
  - An example input filter that removes all tool calls from the conversation history in HandoffInputData.

agents.extensions.handoff_prompt.RECOMMENDED_PROMPT_PREFIX: str
  - A string constant containing a recommended prefix for agent instructions to improve LLM understanding of handoffs.

agents.extensions.handoff_prompt.prompt_with_handoff_instructions(prompt: str) -> str
  - A utility function to automatically add recommended handoff instructions to a given prompt.
```

----------------------------------------

TITLE: Pass Extra Arguments to OpenAI Model Settings in Python
DESCRIPTION: This Python example demonstrates using the `extra_args` parameter within `ModelSettings` to pass additional, non-standard configuration options to the OpenAI model. This allows for advanced customization, such as setting `service_tier` or `user` identifiers, which might not be directly exposed as top-level `ModelSettings` parameters.
SOURCE: https://github.com/openai/openai-agents-python/blob/main/docs/models/index.md#_snippet_4

LANGUAGE: Python
CODE:
```
from agents import Agent, ModelSettings

english_agent = Agent(
    name="English agent",
    instructions="You only speak English",
    model="gpt-4o",
    model_settings=ModelSettings(
        temperature=0.1,
        extra_args={"service_tier": "flex", "user": "user_12345"},
    ),
)
```

----------------------------------------

TITLE: Generating Test Coverage Report (Bash)
DESCRIPTION: This `make` command generates a test coverage report, providing insights into which parts of the codebase are covered by tests. It helps identify areas that may require additional test cases.
SOURCE: https://github.com/openai/openai-agents-python/blob/main/AGENTS.md#_snippet_4

LANGUAGE: bash
CODE:
```
make coverage
```

----------------------------------------

TITLE: Configure Agent with multiple MCP servers
DESCRIPTION: This example illustrates how to associate one or more initialized MCP server instances with an `Agent` during its creation. The Agents SDK will automatically manage tool listing and calling for these servers, making the LLM aware of the tools provided by each server.
SOURCE: https://github.com/openai/openai-agents-python/blob/main/docs/mcp.md#_snippet_1

LANGUAGE: python
CODE:
```
agent=Agent(
    name="Assistant",
    instructions="Use the tools to achieve the task",
    mcp_servers=[mcp_server_1, mcp_server_2]
)
```

----------------------------------------

TITLE: Apply Input Filters to Agent Handoffs in Python
DESCRIPTION: Demonstrates how to use an `input_filter` with the `handoff()` function to modify the conversation history passed to the receiving agent. This example uses a predefined filter (`remove_all_tools`) to clear previous tool calls from the history.
SOURCE: https://github.com/openai/openai-agents-python/blob/main/docs/ja/handoffs.md#_snippet_3

LANGUAGE: python
CODE:
```
from agents import Agent, handoff
from agents.extensions import handoff_filters

agent = Agent(name="FAQ agent")

handoff_obj = handoff(
    agent=agent,
    input_filter=handoff_filters.remove_all_tools,
)
```

----------------------------------------

TITLE: Implement dynamic tool filtering with custom functions
DESCRIPTION: This example provides two functions for dynamic tool filtering: a simple synchronous filter based on tool name patterns and a context-aware filter that utilizes `ToolFilterContext` to access agent and server information for more complex, programmatic filtering logic.
SOURCE: https://github.com/openai/openai-agents-python/blob/main/docs/mcp.md#_snippet_3

LANGUAGE: python
CODE:
```
from agents.mcp import ToolFilterContext

# Simple synchronous filter
def custom_filter(context: ToolFilterContext, tool) -> bool:
    """Example of a custom tool filter."""
    # Filter logic based on tool name patterns
    return tool.name.startswith("allowed_prefix")

# Context-aware filter
def context_aware_filter(context: ToolFilterContext, tool) -> bool:
    """Filter tools based on context information."""
    # Access agent information
    agent_name = context.agent.name

    # Access server information
    server_name = context.server_name

    # Implement your custom filtering logic here
    return some_filtering_logic(agent_name, server_name, tool)
```

----------------------------------------

TITLE: Implement Output Guardrail for Agent
DESCRIPTION: Illustrates the implementation of an output guardrail that uses an auxiliary agent to validate the main agent's response. It defines the guardrail function, integrates it into the agent's configuration, and provides an example of how the guardrail can be triggered by specific output content, preventing undesirable outputs.
SOURCE: https://github.com/openai/openai-agents-python/blob/main/docs/guardrails.md#_snippet_1

LANGUAGE: python
CODE:
```
from pydantic import BaseModel
from agents import (
    Agent,
    GuardrailFunctionOutput,
    OutputGuardrailTripwireTriggered,
    RunContextWrapper,
    Runner,
    output_guardrail,
)
class MessageOutput(BaseModel): # (1)!
    response: str

class MathOutput(BaseModel): # (2)!
    reasoning: str
    is_math: bool

guardrail_agent = Agent(
    name="Guardrail check",
    instructions="Check if the output includes any math.",
    output_type=MathOutput,
)

@output_guardrail
async def math_guardrail(  # (3)!
    ctx: RunContextWrapper, agent: Agent, output: MessageOutput
) -> GuardrailFunctionOutput:
    result = await Runner.run(guardrail_agent, output.response, context=ctx.context)

    return GuardrailFunctionOutput(
        output_info=result.final_output,
        tripwire_triggered=result.final_output.is_math,
    )

agent = Agent( # (4)!
    name="Customer support agent",
    instructions="You are a customer support agent. You help customers with their questions.",
    output_guardrails=[math_guardrail],
    output_type=MessageOutput,
)

async def main():
    # This should trip the guardrail
    try:
        await Runner.run(agent, "Hello, can you help me solve for x: 2x + 3 = 11?")
        print("Guardrail didn't trip - this is unexpected")

    except OutputGuardrailTripwireTriggered:
        print("Math output guardrail tripped")
```

----------------------------------------

TITLE: Filter Conversation History for Agent Handoffs in Python
DESCRIPTION: Demonstrates how to apply an `input_filter` to a handoff, allowing modification of the conversation history seen by the receiving agent. This example uses a predefined filter from `agents.extensions.handoff_filters` to automatically remove all tool calls from the history.
SOURCE: https://github.com/openai/openai-agents-python/blob/main/docs/handoffs.md#_snippet_3

LANGUAGE: python
CODE:
```
from agents import Agent, handoff
from agents.extensions import handoff_filters

agent = Agent(name="FAQ agent")

handoff_obj = handoff(
    agent=agent,
    input_filter=handoff_filters.remove_all_tools, # (1)!
)
```

----------------------------------------

TITLE: Execute Research Bot for Vacation Planning
DESCRIPTION: This command initiates the research bot example script using 'uv run', a tool for executing Python projects. The bot is prompted to research Caribbean vacation spots in April, with a focus on activities like surfing, hiking, and water sports. The output includes a trace ID and a summary of the bot's progress.
SOURCE: https://github.com/openai/openai-agents-python/blob/main/examples/research_bot/sample_outputs/vacation.txt#_snippet_0

LANGUAGE: bash
CODE:
```
$ uv run python -m examples.research_bot.main
What would you like to research? Caribbean vacation spots in April, optimizing for surfing, hiking and water sports
View trace: https://platform.openai.com/traces/trace?trace_id=trace_....
Starting research...
✅ Will perform 15 searches
✅ Searching... 15/15 completed
✅ Finishing report...
✅ Report summary
```

----------------------------------------

TITLE: Updating and Creating Snapshot Tests (Bash)
DESCRIPTION: These `make` commands are used for managing inline snapshot tests. `make snapshots-fix` updates existing snapshots to match current output, while `make snapshots-create` generates new ones. Running `make tests` afterwards is necessary to confirm they pass.
SOURCE: https://github.com/openai/openai-agents-python/blob/main/AGENTS.md#_snippet_5

LANGUAGE: bash
CODE:
```
make snapshots-fix
make snapshots-create
```

----------------------------------------

TITLE: Execute All or Specific Tests using Make and pytest
DESCRIPTION: The `make tests` command runs the entire test suite for the project. For focused development, individual tests can be executed directly using `uv run pytest -s -k <test_name>`, allowing developers to quickly verify changes to specific components.
SOURCE: https://github.com/openai/openai-agents-python/blob/main/AGENTS.md#_snippet_1

LANGUAGE: bash
CODE:
```
make tests
```

LANGUAGE: bash
CODE:
```
uv run pytest -s -k <test_name>
```

----------------------------------------

TITLE: Extract Specific Output from Agent Run Results in Python
DESCRIPTION: This code demonstrates how to implement a `custom_output_extractor` function to process the `RunResult` of a tool-agent. The example shows how to scan the agent's output history in reverse to find and extract a specific JSON payload, providing a robust fallback to an empty JSON object if no suitable output is found.
SOURCE: https://github.com/openai/openai-agents-python/blob/main/docs/tools.md#_snippet_5

LANGUAGE: python
CODE:
```
async def extract_json_payload(run_result: RunResult) -> str:
    # Scan the agent’s outputs in reverse order until we find a JSON-like message from a tool call.
    for item in reversed(run_result.new_items):
        if isinstance(item, ToolCallOutputItem) and item.output.strip().startswith("{"):
            return item.output.strip()
    # Fallback to an empty JSON object if nothing was found
    return "{}"


json_tool = data_agent.as_tool(
    tool_name="get_data_json",
    tool_description="Run the data agent and return only its JSON payload",
    custom_output_extractor=extract_json_payload,
)
```

----------------------------------------

TITLE: Update and Create Inline Snapshots for Tests
DESCRIPTION: These `make` commands are specifically for managing inline snapshot tests. `make snapshots-fix` updates existing snapshots to match current test outputs, while `make snapshots-create` generates new snapshot files for new tests. After updating, `make tests` should be run to confirm all tests pass.
SOURCE: https://github.com/openai/openai-agents-python/blob/main/AGENTS.md#_snippet_3

LANGUAGE: bash
CODE:
```
make snapshots-fix
make snapshots-create
```

----------------------------------------

TITLE: Programmatic Trace and Span Management in OpenAI Agents SDK
DESCRIPTION: This section outlines the methods available for programmatically creating and managing traces and spans within the OpenAI Agents SDK. It covers the recommended context manager approach for traces, options for manual trace control, and the utility of `custom_span()` for integrating user-defined operations into the tracing hierarchy.
SOURCE: https://github.com/openai/openai-agents-python/blob/main/docs/tracing.md#_snippet_2

LANGUAGE: APIDOC
CODE:
```
Trace Creation Methods:
  1. Context Manager (Recommended):
     trace(workflow_name: str, trace_id: str = None, group_id: str = None, disabled: bool = False, metadata: dict = None)
       - Usage: with trace(...) as my_trace: ...
       - Automatically starts and finishes the trace.

  2. Manual Control:
     trace_instance = trace(workflow_name: str, ...)
     trace_instance.start(mark_as_current: bool = True)
     # ... code ...
     trace_instance.finish(reset_current: bool = True)
       - Requires explicit start() and finish() calls.
       - mark_as_current: Sets the trace as the current trace in the contextvar.
       - reset_current: Resets the current trace in the contextvar upon finish.

Span Creation Methods:
  - Automatic: Most spans are generated by default SDK operations (e.g., agent_span, generation_span).
  - Custom: Use custom_span() for user-defined operations.
    custom_span(span_name: str, span_data: dict = None, parent_id: str = None, metadata: dict = None)
      - span_name: The name of the custom span.
      - span_data: Custom data associated with the span.
      - parent_id: The ID of the parent span. If None, uses the current span from contextvar.
      - metadata: Optional dictionary for custom span metadata.
```

----------------------------------------

TITLE: VoicePipeline Class and Event Handling
DESCRIPTION: Comprehensive documentation for the `VoicePipeline` class, detailing its purpose, configuration options, execution methods, and the structure of its streamed results and event types. It covers how to initialize the pipeline, run it with different audio inputs, and process the various events emitted during its operation.
SOURCE: https://github.com/openai/openai-agents-python/blob/main/docs/voice/pipeline.md#_snippet_2

LANGUAGE: APIDOC
CODE:
```
VoicePipeline Class:
  Purpose: Facilitates turning agentic workflows into voice applications by managing speech-to-text, custom logic execution, and text-to-speech.

  Configuration Parameters:
    - workflow: agents.voice.workflow.VoiceWorkflowBase
      Description: The core logic that runs each time new audio is transcribed.
    - speech-to-text model: agents.voice.model.STTModel
      Description: The model used for transcribing audio input into text.
    - text-to-speech model: agents.voice.model.TTSModel
      Description: The model used for converting text output back into audio.
    - config: agents.voice.pipeline_config.VoicePipelineConfig
      Description: Advanced configuration options including model providers, tracing settings (e.g., disabling tracing, audio file uploads, workflow name, trace IDs), and specific settings for TTS/STT models (e.g., prompt, language, data types).

VoicePipeline.run(input) Method:
  Purpose: Executes the voice pipeline with the provided audio input.
  Parameters:
    - input:
      - AudioInput (agents.voice.input.AudioInput)
        Description: Used when a full audio transcript is available and immediate result production is desired. Suitable for pre-recorded audio or push-to-talk scenarios where speaker completion is clear.
      - StreamedAudioInput (agents.voice.input.StreamedAudioInput)
        Description: Used for pushing audio chunks as they are detected, enabling activity detection to determine when a user is done speaking and automatically running the agent workflow at the appropriate time.
  Returns: StreamedAudioResult (agents.voice.result.StreamedAudioResult)
    Description: An object that allows streaming events as they occur during the pipeline run.

StreamedAudioResult Class:
  Purpose: Represents the result of a voice pipeline run, providing an asynchronous stream of events.
  Methods:
    - stream(): Async iterator that yields VoiceStreamEvent objects.

VoiceStreamEvent Types:
  - VoiceStreamEventAudio (agents.voice.events.VoiceStreamEventAudio)
    Description: Contains a chunk of audio output from the pipeline.
  - VoiceStreamEventLifecycle (agents.voice.events.VoiceStreamEventLifecycle)
    Description: Informs about significant lifecycle events during the pipeline's execution, such as 'turn_started' (new transcription processing begins) and 'turn_ended' (all audio dispatched for a turn).
  - VoiceStreamEventError (agents.voice.events.VoiceStreamEventError)
    Description: An event indicating an error occurred during the pipeline's operation.

Usage Example (Event Processing):
  result = await pipeline.run(input)
  async for event in result.stream():
      if event.type == "voice_stream_event_audio":
          # Logic to play audio
      elif event.type == "voice_stream_event_lifecycle":
          # Logic to handle lifecycle events (e.g., mute/unmute microphone based on turn_started/turn_ended)
      elif event.type == "voice_stream_event_error":
          # Logic to handle errors
      ...
```

----------------------------------------

TITLE: OpenAI Agents SDK Tracing Concepts and Configuration
DESCRIPTION: This section provides a comprehensive overview of tracing in the OpenAI Agents SDK, detailing how to enable or disable tracing, the fundamental properties of traces and spans, and the various operations that are automatically traced by default within the SDK.
SOURCE: https://github.com/openai/openai-agents-python/blob/main/docs/tracing.md#_snippet_0

LANGUAGE: APIDOC
CODE:
```
Tracing Configuration:
  - Global Disable: Set environment variable OPENAI_AGENTS_DISABLE_TRACING=1
  - Per-Run Disable: Set agents.run.RunConfig.tracing_disabled = True

Trace Properties:
  - workflow_name (str): Logical workflow or app name (e.g., "Code generation").
  - trace_id (str): Unique ID for the trace (e.g., "trace_<32_alphanumeric>"). Auto-generated if not provided.
  - group_id (str, optional): Optional group ID to link multiple traces (e.g., chat thread ID).
  - disabled (bool): If True, the trace will not be recorded.
  - metadata (dict, optional): Optional dictionary for custom trace metadata.

Span Properties:
  - started_at (timestamp): When the span started.
  - ended_at (timestamp): When the span ended.
  - trace_id (str): ID of the trace the span belongs to.
  - parent_id (str, optional): ID of the parent Span of this Span (if any).
  - span_data (dict): Information specific to the span type (e.g., AgentSpanData, GenerationSpanData).

Default Traced Operations:
  - Runner.{run, run_sync, run_streamed}(): Wrapped in a trace().
  - Agent runs: Wrapped in agent_span().
  - LLM generations: Wrapped in generation_span().
  - Function tool calls: Wrapped in function_span().
  - Guardrails: Wrapped in guardrail_span().
  - Handoffs: Wrapped in handoff_span().
  - Audio inputs (speech-to-text): Wrapped in transcription_span().
  - Audio outputs (text-to-speech): Wrapped in speech_span().
  - Related audio spans: May be parented under a speech_group_span().
```

----------------------------------------

TITLE: Initialize and Run OpenAI Agent for Haiku Generation
DESCRIPTION: This Python snippet demonstrates how to initialize an `Agent` with specific instructions and then use a `Runner` to execute a task asynchronously. It's particularly suited for environments that support top-level `await`, such as Jupyter notebooks, and prints the final output generated by the agent.
SOURCE: https://github.com/openai/openai-agents-python/blob/main/examples/basic/hello_world_jupyter.ipynb#_snippet_0

LANGUAGE: python
CODE:
```
from agents import Agent, Runner

agent = Agent(name="Assistant", instructions="You are a helpful assistant")

# Intended for Jupyter notebooks where there's an existing event loop
result = await Runner.run(agent, "Write a haiku about recursion in programming.") # type: ignore[top-level-await]  # noqa: F704
print(result.final_output)
```

----------------------------------------

TITLE: Agent Class Definition and Methods
DESCRIPTION: Documents the core configuration parameters for initializing an `Agent` instance and its utility methods. It covers essential properties like `name`, `instructions`, `model`, `tools`, `output_type`, `handoffs`, `hooks`, and the `clone()` method for duplicating agents.
SOURCE: https://github.com/openai/openai-agents-python/blob/main/docs/agents.md#_snippet_6

LANGUAGE: APIDOC
CODE:
```
Agent(
  name: str,
  instructions: Union[str, Callable],
  model: str,
  model_settings: Optional[ModelSettings] = None,
  tools: Optional[list] = None,
  output_type: Optional[Type] = None,
  handoffs: Optional[list[Agent]] = None,
  hooks: Optional[AgentHooks] = None
)
  - Description: Initializes a new Agent instance.
  - Parameters:
    - name (str): A required string that identifies your agent.
    - instructions (Union[str, Callable]): The developer message or system prompt. Can be a static string or a function for dynamic instructions.
    - model (str): The Large Language Model (LLM) to use (e.g., "o3-mini").
    - model_settings (Optional[ModelSettings]): Optional parameters to configure model tuning (e.g., temperature, top_p).
    - tools (Optional[list]): A list of tools (e.g., functions decorated with `@function_tool`) that the agent can use.
    - output_type (Optional[Type]): Specifies the desired structured output type (e.g., Pydantic BaseModel, dataclass).
    - handoffs (Optional[list[Agent]]): A list of sub-agents that the agent can delegate tasks to.
    - hooks (Optional[AgentHooks]): An instance of `AgentHooks` to observe and react to agent lifecycle events.

Agent.clone(
  name: Optional[str] = None,
  instructions: Optional[Union[str, Callable]] = None,
  model: Optional[str] = None,
  model_settings: Optional[ModelSettings] = None,
  tools: Optional[list] = None,
  output_type: Optional[Type] = None,
  handoffs: Optional[list[Agent]] = None,
  hooks: Optional[AgentHooks] = None
) -> Agent
  - Description: Creates a duplicate of the current Agent instance, optionally overriding specified properties.
  - Parameters: Any of the Agent initialization parameters can be provided to override the cloned agent's properties.
  - Returns: A new Agent instance with the specified modifications.
```

----------------------------------------

TITLE: Configure Custom OpenAI Client for SDK
DESCRIPTION: Shows how to provide a custom `AsyncOpenAI` client instance to the SDK using `set_default_openai_client()`, allowing for custom `base_url` or other client configurations instead of the default SDK-created client.
SOURCE: https://github.com/openai/openai-agents-python/blob/main/docs/config.md#_snippet_1

LANGUAGE: python
CODE:
```
from openai import AsyncOpenAI
from agents import set_default_openai_client

custom_client = AsyncOpenAI(base_url="...", api_key="...")
set_default_openai_client(custom_client)
```

----------------------------------------

TITLE: Integrating Custom Functions as Agent Tools
DESCRIPTION: This snippet demonstrates how to integrate custom Python functions as tools for an agent using the `@function_tool` decorator. The agent can then invoke these tools based on user input, extending its capabilities beyond simple text generation and enabling interaction with external functionalities.
SOURCE: https://github.com/openai/openai-agents-python/blob/main/README.md#_snippet_5

LANGUAGE: python
CODE:
```
import asyncio

from agents import Agent, Runner, function_tool


@function_tool
def get_weather(city: str) -> str:
    return f"The weather in {city} is sunny."


agent = Agent(
    name="Hello world",
    instructions="You are a helpful agent.",
    tools=[get_weather],
)


async def main():
    result = await Runner.run(agent, input="What's the weather in Tokyo?")
    print(result.final_output)
    # The weather in Tokyo is sunny.


if __name__ == "__main__":
    asyncio.run(main())
```

----------------------------------------

TITLE: Install SDK Dependencies
DESCRIPTION: Installs all necessary project dependencies using the `make sync` command, preparing the environment for development and ensuring all required packages are available.
SOURCE: https://github.com/openai/openai-agents-python/blob/main/README.md#_snippet_7

LANGUAGE: bash
CODE:
```
make sync
```

----------------------------------------

TITLE: Voice Pipeline Workflow Diagram
DESCRIPTION: Illustrates the end-to-end flow of the VoicePipeline, from initial audio input through transcription, custom code execution, text-to-speech conversion, and final audio output.
SOURCE: https://github.com/openai/openai-agents-python/blob/main/docs/voice/pipeline.md#_snippet_0

LANGUAGE: mermaid
CODE:
```
graph LR
    %% Input
    A["🎤 Audio Input"]

    %% Voice Pipeline
    subgraph Voice_Pipeline [Voice Pipeline]
        direction TB
        B["Transcribe (speech-to-text)"]
        C["Your Code"]:::highlight
        D["Text-to-speech"]
        B --> C --> D
    end

    %% Output
    E["🎧 Audio Output"]

    %% Flow
    A --> Voice_Pipeline
    Voice_Pipeline --> E

    %% Custom styling
    classDef highlight fill:#ffcc66,stroke:#333,stroke-width:1px,font-weight:700;
```

----------------------------------------

TITLE: Voice Pipeline Workflow Diagram
DESCRIPTION: Illustrates the three-step process of a Voice Pipeline: Transcribe (speech-to-text), Your Code (agentic workflow), and Text-to-speech, showing the flow from audio input to audio output.
SOURCE: https://github.com/openai/openai-agents-python/blob/main/docs/voice/quickstart.md#_snippet_1

LANGUAGE: mermaid
CODE:
```
graph LR
    %% Input
    A["🎤 Audio Input"]

    %% Voice Pipeline
    subgraph Voice_Pipeline [Voice Pipeline]
        direction TB
        B["Transcribe (speech-to-text)"]
        C["Your Code"]:::highlight
        D["Text-to-speech"]
        B --> C --> D
    end

    %% Output
    E["🎧 Audio Output"]

    %% Flow
    A --> Voice_Pipeline
    Voice_Pipeline --> E

    %% Custom styling
    classDef highlight fill:#ffcc66,stroke:#333,stroke-width:1px,font-weight:700;
```

----------------------------------------

TITLE: Initialize and use MCPServerStdio with filesystem server
DESCRIPTION: This Python snippet demonstrates how to initialize an `MCPServerStdio` instance to connect to a local MCP filesystem server using `npx`. It shows how to set up the server parameters and then call `list_tools()` to retrieve available tools, illustrating the direct interaction with an MCP server.
SOURCE: https://github.com/openai/openai-agents-python/blob/main/docs/ja/mcp.md#_snippet_0

LANGUAGE: python
CODE:
```
from agents.run_context import RunContextWrapper

async with MCPServerStdio(
    params={
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-filesystem", samples_dir],
    }
) as server:
    # 注意：実際には通常は MCP サーバーをエージェントに追加し、
    # フレームワークがツール一覧の取得を自動的に処理するようにします。
    # list_tools() への直接呼び出しには run_context と agent パラメータが必要です。
    run_context = RunContextWrapper(context=None)
    agent = Agent(name="test", instructions="test")
    tools = await server.list_tools(run_context, agent)
```

----------------------------------------

TITLE: Interact with MCP Server Prompts for Agent Instructions
DESCRIPTION: Demonstrates how to programmatically list available prompts from an MCP server and retrieve a specific prompt by name, passing optional arguments. The generated instructions are then used to initialize an `Agent`.
SOURCE: https://github.com/openai/openai-agents-python/blob/main/docs/mcp.md#_snippet_5

LANGUAGE: python
CODE:
```
# List available prompts
prompts_result = await server.list_prompts()
for prompt in prompts_result.prompts:
    print(f"Prompt: {prompt.name} - {prompt.description}")

# Get a specific prompt with parameters
prompt_result = await server.get_prompt(
    "generate_code_review_instructions",
    {"focus": "security vulnerabilities", "language": "python"}
)
instructions = prompt_result.messages[0].content.text

# Use the prompt-generated instructions with an Agent
agent = Agent(
    name="Code Reviewer",
    instructions=instructions,  # Instructions from MCP prompt
    mcp_servers=[server]
)
```

----------------------------------------

TITLE: Function Tool Error Handling Configuration
DESCRIPTION: This section details how to configure error handling for function tools created with `@function_tool`. It explains the default behavior, how to provide a custom error function, and how to explicitly disable automatic error handling to re-raise exceptions for manual processing.
SOURCE: https://github.com/openai/openai-agents-python/blob/main/docs/tools.md#_snippet_6

LANGUAGE: APIDOC
CODE:
```
@function_tool(failure_error_function: Callable[[Exception], str] | None = default_tool_error_function)
  - Configures error handling for the function tool.
  - Parameters:
    - failure_error_function: A callable that takes an exception and returns a string error message to be sent to the LLM.
      - Default: `default_tool_error_function` (sends a generic error message to LLM).
      - Custom: Provide your own function to handle specific error responses.
      - None: Disables automatic error handling; exceptions (e.g., `ModelBehaviorError`, `UserError`) will be re-raised for manual handling.
  - Notes:
    - For manually created `FunctionTool` objects, error handling must be implemented within the `on_invoke_tool` function.
```

----------------------------------------

TITLE: Configure Tracing for Voice Pipelines with VoicePipelineConfig
DESCRIPTION: This snippet details the key configuration fields within `VoicePipelineConfig` that allow for fine-grained control over tracing behavior in voice pipelines, including enabling/disabling tracing, managing sensitive data inclusion, and associating traces with workflows and groups.
SOURCE: https://github.com/openai/openai-agents-python/blob/main/docs/voice/tracing.md#_snippet_0

LANGUAGE: APIDOC
CODE:
```
VoicePipelineConfig Tracing Fields:

- tracing_disabled:
    Type: boolean
    Description: Controls whether tracing is disabled. By default, tracing is enabled.
    Default: false

- trace_include_sensitive_data:
    Type: boolean
    Description: Controls whether traces include potentially sensitive data, like audio transcripts. This is specifically for the voice pipeline, and not for anything that goes on inside your Workflow.

- trace_include_sensitive_audio_data:
    Type: boolean
    Description: Controls whether traces include audio data.

- workflow_name:
    Type: string
    Description: The name of the trace workflow.

- group_id:
    Type: string
    Description: The group_id of the trace, which lets you link multiple traces.

- trace_metadata:
    Type: dictionary
    Description: Additional metadata to include with the trace.
```

----------------------------------------

TITLE: Define and Orchestrate Translation Agents as Tools in Python
DESCRIPTION: This snippet demonstrates how to define multiple specialized agents (e.g., for Spanish and French translation) and then orchestrate them using a central agent. It shows how to convert agents into callable tools using `agent.as_tool()` and execute them via `Runner.run()` to achieve complex, multi-agent workflows.
SOURCE: https://github.com/openai/openai-agents-python/blob/main/docs/tools.md#_snippet_3

LANGUAGE: python
CODE:
```
from agents import Agent, Runner
import asyncio

spanish_agent = Agent(
    name="Spanish agent",
    instructions="You translate the user's message to Spanish",
)

french_agent = Agent(
    name="French agent",
    instructions="You translate the user's message to French",
)

orchestrator_agent = Agent(
    name="orchestrator_agent",
    instructions=(
        "You are a translation agent. You use the tools given to you to translate."
        "If asked for multiple translations, you call the relevant tools."
    ),
    tools=[
        spanish_agent.as_tool(
            tool_name="translate_to_spanish",
            tool_description="Translate the user's message to Spanish",
        ),
        french_agent.as_tool(
            tool_name="translate_to_french",
            tool_description="Translate the user's message to French",
        ),
    ],
)

async def main():
    result = await Runner.run(orchestrator_agent, input="Say 'Hello, how are you?' in Spanish.")
    print(result.final_output)
```

----------------------------------------

TITLE: Install OpenAI Agents SDK
DESCRIPTION: Installs the OpenAI Agents SDK using the pip package manager, making it available for use in Python projects.
SOURCE: https://github.com/openai/openai-agents-python/blob/main/docs/index.md#_snippet_0

LANGUAGE: bash
CODE:
```
pip install openai-agents
```

----------------------------------------

TITLE: Build a Voice Assistant with OpenAI Agents and Tool Use
DESCRIPTION: This Python code demonstrates how to set up an AI agent with a custom tool (`get_weather`), handle language-specific handoffs (e.g., to a Spanish agent), and integrate with a voice pipeline for real-time audio interaction. It utilizes `asyncio` for asynchronous operations and `sounddevice` for audio input/output, allowing the agent to speak and respond to user input.
SOURCE: https://github.com/openai/openai-agents-python/blob/main/docs/voice/quickstart.md#_snippet_5

LANGUAGE: python
CODE:
```
import asyncio
import random

import numpy as np
import sounddevice as sd

from agents import (
    Agent,
    function_tool,
    set_tracing_disabled,
)
from agents.voice import (
    AudioInput,
    SingleAgentVoiceWorkflow,
    VoicePipeline,
)
from agents.extensions.handoff_prompt import prompt_with_handoff_instructions


@function_tool
def get_weather(city: str) -> str:
    """Get the weather for a given city."""
    print(f"[debug] get_weather called with city: {city}")
    choices = ["sunny", "cloudy", "rainy", "snowy"]
    return f"The weather in {city} is {random.choice(choices)}."


spanish_agent = Agent(
    name="Spanish",
    handoff_description="A spanish speaking agent.",
    instructions=prompt_with_handoff_instructions(
        "You're speaking to a human, so be polite and concise. Speak in Spanish.",
    ),
    model="gpt-4o-mini",
)

agent = Agent(
    name="Assistant",
    instructions=prompt_with_handoff_instructions(
        "You're speaking to a human, so be polite and concise. If the user speaks in Spanish, handoff to the spanish agent.",
    ),
    model="gpt-4o-mini",
    handoffs=[spanish_agent],
    tools=[get_weather],
)


async def main():
    pipeline = VoicePipeline(workflow=SingleAgentVoiceWorkflow(agent))
    buffer = np.zeros(24000 * 3, dtype=np.int16)
    audio_input = AudioInput(buffer=buffer)

    result = await pipeline.run(audio_input)

    # Create an audio player using `sounddevice`
    player = sd.OutputStream(samplerate=24000, channels=1, dtype=np.int16)
    player.start()

    # Play the audio stream as it comes in
    async for event in result.stream():
        if event.type == "voice_stream_event_audio":
            player.write(event.data)


if __name__ == "__main__":
    asyncio.run(main())
```

----------------------------------------

TITLE: Configure Sensitive Data Tracing in OpenAI Agents
DESCRIPTION: This section details how to control the capture of potentially sensitive data within LLM generation and function call spans, as well as audio data in voice spans, by adjusting specific configuration flags.
SOURCE: https://github.com/openai/openai-agents-python/blob/main/docs/tracing.md#_snippet_3

LANGUAGE: APIDOC
CODE:
```
RunConfig.trace_include_sensitive_data
  - Type: Boolean
  - Description: Controls whether inputs/outputs of LLM generation and function call spans are captured. Set to `False` to disable capturing sensitive data.

VoicePipelineConfig.trace_include_sensitive_audio_data
  - Type: Boolean
  - Description: Controls whether base64-encoded PCM data for input and output audio is captured in Audio spans. Set to `False` to disable capturing sensitive audio data.
```

----------------------------------------

TITLE: Run all project tests
DESCRIPTION: Executes the entire test suite for the project. Ensure `uv` is installed and `make sync` has been run prior to execution to set up the environment.
SOURCE: https://github.com/openai/openai-agents-python/blob/main/tests/README.md#_snippet_0

LANGUAGE: Shell
CODE:
```
make tests
```

----------------------------------------

TITLE: Execute Agent Orchestration Workflow
DESCRIPTION: This asynchronous function demonstrates how to run an agent orchestration using the `Runner.run` method. It initiates a workflow with a `triage_agent` and a user query, then prints the final output from the orchestrated agents.
SOURCE: https://github.com/openai/openai-agents-python/blob/main/docs/quickstart.md#_snippet_7

LANGUAGE: python
CODE:
```
from agents import Runner

async def main():
    result = await Runner.run(triage_agent, "What is the capital of France?")
    print(result.final_output)
```

----------------------------------------

TITLE: RunResult and RunResultBase Object Properties
DESCRIPTION: Documentation for the `RunResult` and `RunResultBase` objects, which encapsulate the outcome of agent runs, providing access to final outputs, intermediate items, and run metadata. These objects are returned by the `Runner.run` methods.
SOURCE: https://github.com/openai/openai-agents-python/blob/main/docs/results.md#_snippet_0

LANGUAGE: APIDOC
CODE:
```
RunResult Objects:
  - RunResult: Returned by Runner.run or Runner.run_sync.
  - RunResultStreaming: Returned by Runner.run_streamed.
  - Both inherit from RunResultBase.

RunResultBase Properties and Methods:

final_output: Any
  - Contains the final output of the last agent that ran.
  - Type: str (if no output_type defined) or last_agent.output_type (if defined).
  - Note: Type is Any due to potential handoffs.

to_input_list(): list
  - Converts the run result into an input list.
  - Concatenates original input with items generated during the run.
  - Useful for chaining agent runs or looping.

last_agent: Agent
  - Contains the last agent that ran.
  - Useful for re-using the agent in subsequent turns (e.g., after a handoff).

new_items: list[RunItem]
  - Contains new items generated during the run.
  - Each item is a RunItem.

input_guardrail_results: GuardrailResult
  - Contains results of input guardrails, if any.
  - Useful for logging or storing guardrail outcomes.

output_guardrail_results: GuardrailResult
  - Contains results of output guardrails, if any.
  - Useful for logging or storing guardrail outcomes.

raw_responses: list[ModelResponse]
  - Contains the raw ModelResponse objects generated by the LLM.

input: Any
  - Contains the original input provided to the run method.
```

----------------------------------------

TITLE: Initialize and use MCPServerStdio for local filesystem access
DESCRIPTION: This snippet demonstrates how to initialize an `MCPServerStdio` instance to connect to a local filesystem server using `npx`. It shows how to set up the server command and arguments, and then how to list tools from the server within a `RunContextWrapper`.
SOURCE: https://github.com/openai/openai-agents-python/blob/main/docs/mcp.md#_snippet_0

LANGUAGE: python
CODE:
```
from agents.run_context import RunContextWrapper

async with MCPServerStdio(
    params={
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-filesystem", samples_dir],
    }
) as server:
    # Note: In practice, you typically add the server to an Agent
    # and let the framework handle tool listing automatically.
    # Direct calls to list_tools() require run_context and agent parameters.
    run_context = RunContextWrapper(context=None)
    agent = Agent(name="test", instructions="test")
    tools = await server.list_tools(run_context, agent)
```

----------------------------------------

TITLE: OpenAI Agent Run Configuration Parameters
DESCRIPTION: This section details the various parameters available within the `run_config` object, which allows global settings to be applied to an agent run, overriding agent-specific configurations. These parameters control aspects like model selection, guardrails, tracing, and metadata.
SOURCE: https://github.com/openai/openai-agents-python/blob/main/docs/running_agents.md#_snippet_1

LANGUAGE: APIDOC
CODE:
```
RunConfig Parameters:
- model: Allows setting a global LLM model to use, irrespective of what `model` each Agent has.
- model_provider: A model provider for looking up model names, which defaults to OpenAI.
- model_settings: Overrides agent-specific settings. For example, you can set a global `temperature` or `top_p`.
- input_guardrails, output_guardrails: A list of input or output guardrails to include on all runs.
- handoff_input_filter: A global input filter to apply to all handoffs, if the handoff doesn't already have one. The input filter allows you to edit the inputs that are sent to the new agent. See the documentation in `Handoff.input_filter` for more details.
- tracing_disabled: Allows you to disable tracing for the entire run.
- trace_include_sensitive_data: Configures whether traces will include potentially sensitive data, such as LLM and tool call inputs/outputs.
- workflow_name, trace_id, group_id: Sets the tracing workflow name, trace ID and trace group ID for the run. We recommend at least setting `workflow_name`. The group ID is an optional field that lets you link traces across multiple runs.
- trace_metadata: Metadata to include on all traces.
```

----------------------------------------

TITLE: Customizing Tracing Processors in OpenAI Agents
DESCRIPTION: This section describes the high-level architecture for tracing in OpenAI Agents, including the roles of `TraceProvider`, `BatchTraceProcessor`, and `BackendSpanExporter`. It also explains how to customize the default tracing setup by adding or replacing trace processors to send traces to alternative or additional backends.
SOURCE: https://github.com/openai/openai-agents-python/blob/main/docs/tracing.md#_snippet_4

LANGUAGE: APIDOC
CODE:
```
TraceProvider
  - Role: Global component responsible for creating traces at initialization.
  - Configuration: Typically configured with a `BatchTraceProcessor`.

BatchTraceProcessor
  - Role: Handles sending traces and spans in batches to a `BackendSpanExporter`.

BackendSpanExporter
  - Role: Exports spans and traces to the OpenAI backend in batches.

add_trace_processor()
  - Purpose: Adds an additional trace processor to the existing setup.
  - Behavior: The added processor will receive traces and spans as they are ready, allowing for custom processing in addition to sending traces to OpenAI's backend.

set_trace_processors()
  - Purpose: Replaces the default trace processors with a custom set of processors.
  - Behavior: Traces will only be sent to the OpenAI backend if a `TracingProcessor` that performs this action is explicitly included in the new set of processors. Provides full control over trace processing and export.
```

----------------------------------------

TITLE: Provide Dynamic Agent Instructions via a Function
DESCRIPTION: Explains how to supply agent instructions dynamically using a Python function. The function receives the agent and context, allowing for personalized or context-aware prompt generation based on the current run's state or user-specific information.
SOURCE: https://github.com/openai/openai-agents-python/blob/main/docs/agents.md#_snippet_4

LANGUAGE: Python
CODE:
```
def dynamic_instructions(
    context: RunContextWrapper[UserContext], agent: Agent[UserContext]
) -> str:
    return f"The user's name is {context.context.name}. Help them with their questions."


agent = Agent[
    UserContext
](
    name="Triage agent",
    instructions=dynamic_instructions,
)
```

----------------------------------------

TITLE: Agents SDK Handoff Function and Related Properties
DESCRIPTION: Comprehensive documentation for the `handoff()` function and related properties within the Agents SDK, detailing parameters for customizing agent delegation, tool naming, descriptions, and input handling. This includes the `Agent.handoffs` parameter, `Handoff` utility methods, and input filtering mechanisms.
SOURCE: https://github.com/openai/openai-agents-python/blob/main/docs/handoffs.md#_snippet_5

LANGUAGE: APIDOC
CODE:
```
handoff(
    agent: Agent,
    tool_name_override: Optional[str] = None,
    tool_description_override: Optional[str] = None,
    on_handoff: Optional[Callable] = None,
    input_type: Optional[Type[BaseModel]] = None,
    input_filter: Optional[Callable] = None
)
  - Creates a Handoff object for agent delegation.
  - Parameters:
    - agent (Agent): The agent to which tasks will be handed off.
    - tool_name_override (Optional[str]): Overrides the default tool name (transfer_to_<agent_name>).
    - tool_description_override (Optional[str]): Overrides the default tool description.
    - on_handoff (Optional[Callable]): A callback function executed when the handoff is invoked. Receives RunContextWrapper and optionally LLM generated input. Useful for pre-handoff data fetching.
    - input_type (Optional[Type[BaseModel]]): The Pydantic BaseModel type for structured input expected by the handoff. Enables the LLM to provide typed data.
    - input_filter (Optional[Callable]): A function that receives HandoffInputData and returns a new HandoffInputData, used to filter the conversation history seen by the next agent.

Agent.handoffs: List[Union[Agent, Handoff]]
  - Parameter for the Agent class constructor to define a list of agents or Handoff objects for delegation.

Handoff.default_tool_name(): str
  - Static method to generate the default tool name for a handoff (e.g., 'transfer_to_<agent_name>').

Handoff.default_tool_description(): str
  - Static method to generate the default tool description for a handoff.

Handoff.input_filter: Callable
  - Property of the Handoff object to set a function for filtering input data before it reaches the target agent.

HandoffInputData: object
  - Data structure representing the input received by a handoff filter function.

agents.extensions.handoff_filters: Module
  - A module containing common predefined input filter functions (e.g., `remove_all_tools`) for handoffs.

agents.extensions.handoff_prompt.RECOMMENDED_PROMPT_PREFIX: str
  - A string constant containing recommended prompt instructions for LLMs regarding handoffs, to be included in agent instructions.

agents.extensions.handoff_prompt.prompt_with_handoff_instructions(prompt: str) -> str
  - Function to automatically add recommended handoff instructions to an existing agent prompt string.
```

----------------------------------------

TITLE: Configuring LLM Agent Tool Usage and Behavior
DESCRIPTION: This section details the configuration options available for controlling an LLM agent's tool selection and its subsequent behavior after a tool call, including preventing infinite loops.
SOURCE: https://github.com/openai/openai-agents-python/blob/main/docs/agents.md#_snippet_7

LANGUAGE: APIDOC
CODE:
```
ModelSettings.tool_choice:
  Description: Controls whether and which tool the LLM is allowed or required to use.
  Valid Values:
    - "auto": Allows the LLM to decide whether or not to use a tool.
    - "required": Requires the LLM to use a tool, intelligently deciding which one.
    - "none": Requires the LLM to not use any tool.
    - "<tool_name>": (e.g., "my_tool") Requires the LLM to use the specified tool.

Agent.reset_tool_choice:
  Description: Configures the behavior of resetting 'tool_choice' after a tool call.
  Default Behavior: Automatically resets 'tool_choice' to "auto" after a tool call to prevent infinite loops.
  Purpose: Prevents scenarios where tool results lead to continuous tool calls due to a fixed 'tool_choice' setting.

Agent.tool_use_behavior:
  Description: Defines the agent's behavior immediately after a tool call.
  Valid Values:
    - "stop_on_first_tool": Directly uses the tool output as the final response without further LLM processing.
  Purpose: Allows the agent to stop processing and return the tool output immediately, bypassing further LLM interaction.
```

----------------------------------------

TITLE: Run Voice Pipeline and Stream Audio Output
DESCRIPTION: Demonstrates how to run the initialized `VoicePipeline` with a simulated audio input (3 seconds of silence) and asynchronously stream the resulting audio output using the `sounddevice` library.
SOURCE: https://github.com/openai/openai-agents-python/blob/main/docs/voice/quickstart.md#_snippet_4

LANGUAGE: python
CODE:
```
import numpy as np
import sounddevice as sd
from agents.voice import AudioInput

# For simplicity, we'll just create 3 seconds of silence
# In reality, you'd get microphone data
buffer = np.zeros(24000 * 3, dtype=np.int16)
audio_input = AudioInput(buffer=buffer)

result = await pipeline.run(audio_input)

# Create an audio player using `sounddevice`
player = sd.OutputStream(samplerate=24000, channels=1, dtype=np.int16)
player.start()

# Play the audio stream as it comes in
async for event in result.stream():
    if event.type == "voice_stream_event_audio":
        player.write(event.data)
```

----------------------------------------

TITLE: Set up Python Environment with uv
DESCRIPTION: This snippet shows how to create and activate a Python virtual environment using `uv`, a faster alternative to `venv`. It provides a quick way to set up an isolated environment for project dependencies.
SOURCE: https://github.com/openai/openai-agents-python/blob/main/README.md#_snippet_1

LANGUAGE: bash
CODE:
```
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

----------------------------------------

TITLE: Initialize Voice Pipeline with Single Agent Workflow
DESCRIPTION: Sets up a `VoicePipeline` using `SingleAgentVoiceWorkflow` to integrate a previously defined agent into the voice processing flow, preparing it for audio input and output.
SOURCE: https://github.com/openai/openai-agents-python/blob/main/docs/voice/quickstart.md#_snippet_3

LANGUAGE: python
CODE:
```
from agents.voice import SingleAgentVoiceWorkflow, VoicePipeline
pipeline = VoicePipeline(workflow=SingleAgentVoiceWorkflow(agent))
```

----------------------------------------

TITLE: Define Asynchronous Tool Filter and Configure MCP Server
DESCRIPTION: Illustrates how to create an asynchronous tool filter function that interacts with `ToolFilterContext` and integrate it into an `MCPServerStdio` instance. It also shows the configuration for launching the MCP server via `npx`.
SOURCE: https://github.com/openai/openai-agents-python/blob/main/docs/mcp.md#_snippet_4

LANGUAGE: python
CODE:
```
async def async_filter(context: ToolFilterContext, tool) -> bool:
    """Example of an asynchronous filter."""
    # Perform async operations if needed
    result = await some_async_check(context, tool)
    return result

server = MCPServerStdio(
    params={
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-filesystem", samples_dir],
    },
    tool_filter=custom_filter  # or context_aware_filter or async_filter
)
```

----------------------------------------

TITLE: Processing Voice Pipeline Results
DESCRIPTION: Demonstrates how to asynchronously iterate through events returned by a VoicePipeline run. It shows handling different event types, including audio chunks, lifecycle notifications, and errors, allowing for real-time interaction and feedback.
SOURCE: https://github.com/openai/openai-agents-python/blob/main/docs/voice/pipeline.md#_snippet_1

LANGUAGE: python
CODE:
```
result = await pipeline.run(input)

async for event in result.stream():
    if event.type == "voice_stream_event_audio":
        # play audio
    elif event.type == "voice_stream_event_lifecycle":
        # lifecycle
    elif event.type == "voice_stream_event_error"
        # error
    ...
```

----------------------------------------

TITLE: Create a Basic Agent Handoff in Python
DESCRIPTION: Demonstrates how to initialize agents and configure a basic handoff using the `Agent` class and the `handoff()` function. It shows both direct agent inclusion in the `handoffs` parameter and explicit `handoff()` function usage for delegation.
SOURCE: https://github.com/openai/openai-agents-python/blob/main/docs/handoffs.md#_snippet_0

LANGUAGE: python
CODE:
```
from agents import Agent, handoff

billing_agent = Agent(name="Billing agent")
refund_agent = Agent(name="Refund agent")

# (1)!
triage_agent = Agent(name="Triage agent", handoffs=[billing_agent, handoff(refund_agent)])
```

----------------------------------------

TITLE: Install OpenAI Agents SDK
DESCRIPTION: This command installs the OpenAI Agents SDK using pip, making the necessary libraries available for developing agent-based applications. Alternative package managers like `uv` can also be used.
SOURCE: https://github.com/openai/openai-agents-python/blob/main/docs/quickstart.md#_snippet_2

LANGUAGE: bash
CODE:
```
pip install openai-agents # or `uv add openai-agents`, etc
```

----------------------------------------

TITLE: OpenAI Agents SDK Exception Hierarchy Overview
DESCRIPTION: This section provides an overview of the custom exception classes raised by the OpenAI Agents Python SDK. It details the purpose of each exception, from the base `AgentsException` to specific errors like `MaxTurnsExceeded`, `ModelBehaviorError`, `UserError`, and exceptions related to guardrail tripwires.
SOURCE: https://github.com/openai/openai-agents-python/blob/main/docs/running_agents.md#_snippet_3

LANGUAGE: APIDOC
CODE:
```
- AgentsException: Base class for all exceptions raised in the SDK.
- MaxTurnsExceeded: Raised when the run exceeds the `max_turns` passed to the run methods.
- ModelBehaviorError: Raised when the model produces invalid outputs, e.g. malformed JSON or using non-existent tools.
- UserError: Raised when you (the person writing code using the SDK) make an error using the SDK.
- InputGuardrailTripwireTriggered, OutputGuardrailTripwireTriggered: Raised when a guardrail is tripped.
```

----------------------------------------

TITLE: Run Interactive Demo Loop for OpenAI Agent
DESCRIPTION: Demonstrates how to use `run_demo_loop` from the OpenAI Agents SDK to interactively test an `Agent` instance. It initializes an agent with specific instructions and then enters a loop to process user input, maintaining conversation history and streaming model output. Users can exit the loop by typing 'quit', 'exit', or pressing Ctrl-D.
SOURCE: https://github.com/openai/openai-agents-python/blob/main/docs/repl.md#_snippet_0

LANGUAGE: python
CODE:
```
import asyncio
from agents import Agent, run_demo_loop

async def main() -> None:
    agent = Agent(name="Assistant", instructions="You are a helpful assistant.")
    await run_demo_loop(agent)

if __name__ == "__main__":
    asyncio.run(main())
```

----------------------------------------

TITLE: RunItem and Derived Item Types
DESCRIPTION: Documentation for the `RunItem` base class and its specific derived types, representing different kinds of outputs or events generated during an agent's execution. These items are typically found within the `new_items` property of a `RunResultBase` object.
SOURCE: https://github.com/openai/openai-agents-python/blob/main/docs/results.md#_snippet_1

LANGUAGE: APIDOC
CODE:
```
RunItem Types (contained within RunResultBase.new_items):

RunItem: Base class for items generated during an agent run.
  - Wraps the raw item generated by the LLM.

MessageOutputItem: RunItem
  - Indicates a message from the LLM.
  - Raw item: The message generated.

HandoffCallItem: RunItem
  - Indicates that the LLM called the handoff tool.
  - Raw item: The tool call item from the LLM.

HandoffOutputItem: RunItem
  - Indicates that a handoff occurred.
  - Raw item: The tool response to the handoff tool call.
  - Additional properties: source/target agents.

ToolCallItem: RunItem
  - Indicates that the LLM invoked a tool.

ToolCallOutputItem: RunItem
  - Indicates that a tool was called.
  - Raw item: The tool response.
  - Additional properties: tool output.

ReasoningItem: RunItem
  - Indicates a reasoning item from the LLM.
  - Raw item: The reasoning generated.
```

----------------------------------------

TITLE: Set up Python Environment with venv
DESCRIPTION: This snippet demonstrates how to create and activate a Python virtual environment using the `venv` module. This isolates project dependencies from the system-wide Python installation, ensuring a clean development environment.
SOURCE: https://github.com/openai/openai-agents-python/blob/main/README.md#_snippet_0

LANGUAGE: bash
CODE:
```
python -m venv env
source env/bin/activate  # On Windows: env\Scripts\activate
```

----------------------------------------

TITLE: Integrate Recommended Handoff Prompts in Agent Instructions
DESCRIPTION: Explains how to include a recommended prompt prefix in an agent's instructions to ensure LLMs properly understand handoff mechanisms. This improves the reliability and effectiveness of agent delegation by providing clear guidance to the language model.
SOURCE: https://github.com/openai/openai-agents-python/blob/main/docs/handoffs.md#_snippet_4

LANGUAGE: python
CODE:
```
from agents import Agent
from agents.extensions.handoff_prompt import RECOMMENDED_PROMPT_PREFIX

billing_agent = Agent(
    name="Billing agent",
    instructions=f"""{RECOMMENDED_PROMPT_PREFIX}
    <Fill in the rest of your prompt here>.""",
)
```

----------------------------------------

TITLE: Enable Verbose Standard Output Logging
DESCRIPTION: Demonstrates how to enable verbose debug logging to standard output for the SDK using `enable_verbose_stdout_logging()`.
SOURCE: https://github.com/openai/openai-agents-python/blob/main/docs/config.md#_snippet_5

LANGUAGE: python
CODE:
```
from agents import enable_verbose_stdout_logging

enable_verbose_stdout_logging()
```

----------------------------------------

TITLE: Create Project Directory and Python Virtual Environment
DESCRIPTION: This command sequence initializes a new project directory and sets up a Python virtual environment within it. This isolates project dependencies from the system-wide Python installation, ensuring a clean development environment.
SOURCE: https://github.com/openai/openai-agents-python/blob/main/docs/quickstart.md#_snippet_0

LANGUAGE: bash
CODE:
```
mkdir my_project
cd my_project
python -m venv .venv
```

----------------------------------------

TITLE: Run Individual Development Checks
DESCRIPTION: Provides commands to run specific development checks independently, allowing developers to focus on unit tests, type checking with MyPy, code linting, or style formatting checks as needed.
SOURCE: https://github.com/openai/openai-agents-python/blob/main/README.md#_snippet_9

LANGUAGE: bash
CODE:
```
make tests  # run tests
make mypy   # run typechecker
make lint   # run linter
make format-check # run style checker
```

----------------------------------------

TITLE: Run All Development Checks
DESCRIPTION: Executes a comprehensive suite of development checks, including unit tests, code linting, and type checking, to ensure code quality and adherence to project standards.
SOURCE: https://github.com/openai/openai-agents-python/blob/main/README.md#_snippet_8

LANGUAGE: bash
CODE:
```
make check
```

----------------------------------------

TITLE: Apply static tool filtering to an MCP server
DESCRIPTION: This snippet shows how to use `create_static_tool_filter` to control which tools an MCP server exposes to an Agent. It demonstrates both allowlisting (`allowed_tool_names`) and blocklisting (`blocked_tool_names`) of tools based on their names, explaining the processing order when both are configured.
SOURCE: https://github.com/openai/openai-agents-python/blob/main/docs/mcp.md#_snippet_2

LANGUAGE: python
CODE:
```
from agents.mcp import create_static_tool_filter

# Only expose specific tools from this server
server = MCPServerStdio(
    params={
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-filesystem", samples_dir],
    },
    tool_filter=create_static_tool_filter(
        allowed_tool_names=["read_file", "write_file"]
    )
)

# Exclude specific tools from this server
server = MCPServerStdio(
    params={
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-filesystem", samples_dir],
    },
    tool_filter=create_static_tool_filter(
        blocked_tool_names=["delete_file"]
    )
)
```

----------------------------------------

TITLE: Configure Agent for Structured Pydantic Output
DESCRIPTION: Shows how to specify a structured output type for an agent using Pydantic. By setting `output_type` to a Pydantic `BaseModel` (like `CalendarEvent`), the agent is instructed to produce structured JSON-like responses instead of plain text, leveraging OpenAI's structured outputs feature.
SOURCE: https://github.com/openai/openai-agents-python/blob/main/docs/agents.md#_snippet_2

LANGUAGE: Python
CODE:
```
from pydantic import BaseModel
from agents import Agent


class CalendarEvent(BaseModel):
    name: str
    date: str
    participants: list[str]

agent = Agent(
    name="Calendar extractor",
    instructions="Extract calendar events from text",
    output_type=CalendarEvent,
)
```

----------------------------------------

TITLE: Define Agent Context with a Custom Dataclass
DESCRIPTION: Illustrates how to define a custom context object using a Python dataclass (`UserContext`) and associate it with an `Agent`. This pattern enables dependency injection and state management, allowing agents to access shared data or services during their execution.
SOURCE: https://github.com/openai/openai-agents-python/blob/main/docs/agents.md#_snippet_1

LANGUAGE: Python
CODE:
```
from dataclasses import dataclass

@dataclass
class UserContext:
    uid: str
    is_pro_user: bool

    async def fetch_purchases() -> list:
        return ...

agent = Agent[UserContext](
    ...,
)
```

----------------------------------------

TITLE: Set Model Temperature for OpenAI Agent in Python
DESCRIPTION: This Python snippet illustrates how to configure an `Agent` with specific `ModelSettings`, such as `temperature`. By passing a `ModelSettings` object to the `model_settings` parameter, users can fine-tune the behavior of the underlying LLM, influencing the randomness and creativity of its outputs.
SOURCE: https://github.com/openai/openai-agents-python/blob/main/docs/models/index.md#_snippet_3

LANGUAGE: Python
CODE:
```
from agents import Agent, ModelSettings

english_agent = Agent(
    name="English agent",
    instructions="You only speak English",
    model="gpt-4o",
    model_settings=ModelSettings(temperature=0.1),
)
```

----------------------------------------

TITLE: Integrate Recommended Handoff Prompt Prefix in Python
DESCRIPTION: Illustrates how to include a recommended prompt prefix (`RECOMMENDED_PROMPT_PREFIX`) in an agent's instructions. This helps the LLM understand handoffs correctly and ensures proper behavior when delegating tasks.
SOURCE: https://github.com/openai/openai-agents-python/blob/main/docs/ja/handoffs.md#_snippet_4

LANGUAGE: python
CODE:
```
from agents import Agent
from agents.extensions.handoff_prompt import RECOMMENDED_PROMPT_PREFIX

billing_agent = Agent(
    name="Billing agent",
    instructions=f"""{RECOMMENDED_PROMPT_PREFIX}
    <Fill in the rest of your prompt here>.""",
)
```

----------------------------------------

TITLE: Run Static Voice Demo Application
DESCRIPTION: This command executes the static voice demo application using Python's module execution feature. It initiates the voice pipeline for interactive use.
SOURCE: https://github.com/openai/openai-agents-python/blob/main/examples/voice/static/README.md#_snippet_0

LANGUAGE: bash
CODE:
```
python -m examples.voice.static.main
```

----------------------------------------

TITLE: Orchestrate Agents with Handoffs for Delegation
DESCRIPTION: Demonstrates how to configure an agent (`triage_agent`) to delegate tasks to specialized sub-agents (`booking_agent`, `refund_agent`) based on user queries. This powerful pattern enables the orchestration of modular, specialized agents that excel at single tasks.
SOURCE: https://github.com/openai/openai-agents-python/blob/main/docs/agents.md#_snippet_3

LANGUAGE: Python
CODE:
```
from agents import Agent

booking_agent = Agent(...)
refund_agent = Agent(...)

triage_agent = Agent(
    name="Triage agent",
    instructions=(
        "Help the user with their questions."
        "If they ask about booking, handoff to the booking agent."
        "If they ask about refunds, handoff to the refund agent."
    ),
    handoffs=[booking_agent, refund_agent],
)
```

----------------------------------------

TITLE: Define Agents with Handoff and Function Tool
DESCRIPTION: Defines two `Agent` instances, one for general assistance and another for Spanish language handling, demonstrating agent handoff and the integration of a `function_tool` for retrieving weather information.
SOURCE: https://github.com/openai/openai-agents-python/blob/main/docs/voice/quickstart.md#_snippet_2

LANGUAGE: python
CODE:
```
import asyncio
import random

from agents import (
    Agent,
    function_tool,
)
from agents.extensions.handoff_prompt import prompt_with_handoff_instructions



@function_tool
def get_weather(city: str) -> str:
    """Get the weather for a given city."""
    print(f"[debug] get_weather called with city: {city}")
    choices = ["sunny", "cloudy", "rainy", "snowy"]
    return f"The weather in {city} is {random.choice(choices)}."


spanish_agent = Agent(
    name="Spanish",
    handoff_description="A spanish speaking agent.",
    instructions=prompt_with_handoff_instructions(
        "You're speaking to a human, so be polite and concise. Speak in Spanish.",
    ),
    model="gpt-4o-mini",
)

agent = Agent(
    name="Assistant",
    instructions=prompt_with_handoff_instructions(
        "You're speaking to a human, so be polite and concise. If the user speaks in Spanish, handoff to the spanish agent.",
    ),
    model="gpt-4o-mini",
    handoffs=[spanish_agent],
    tools=[get_weather],
)
```

----------------------------------------

TITLE: Clone an Agent and Modify Properties
DESCRIPTION: Illustrates the use of the `clone()` method to duplicate an existing agent instance. This allows for creating new agents based on an existing configuration while optionally overriding specific properties like name and instructions, facilitating rapid iteration and variant creation.
SOURCE: https://github.com/openai/openai-agents-python/blob/main/docs/agents.md#_snippet_5

LANGUAGE: Python
CODE:
```
pirate_agent = Agent(
    name="Pirate",
    instructions="Write like a pirate",
    model="o3-mini",
)

robot_agent = pirate_agent.clone(
    name="Robot",
    instructions="Write like a robot",
)
```

----------------------------------------

TITLE: Define Multiple OpenAI Agents with Handoff Descriptions
DESCRIPTION: This code illustrates the creation of multiple `Agent` instances, each with a specific role. The `handoff_description` parameter provides additional context, aiding in the routing and orchestration of agents within a multi-agent system.
SOURCE: https://github.com/openai/openai-agents-python/blob/main/docs/quickstart.md#_snippet_5

LANGUAGE: python
CODE:
```
from agents import Agent

history_tutor_agent = Agent(
    name="History Tutor",
    handoff_description="Specialist agent for historical questions",
    instructions="You provide assistance with historical queries. Explain important events and context clearly.",
)

math_tutor_agent = Agent(
    name="Math Tutor",
    handoff_description="Specialist agent for math questions",
    instructions="You provide help with math problems. Explain your reasoning at each step and include examples",
)
```

----------------------------------------

TITLE: Disable Tracing in SDK
DESCRIPTION: Shows how to completely disable the SDK's tracing functionality by calling `set_tracing_disabled()` with `True`.
SOURCE: https://github.com/openai/openai-agents-python/blob/main/docs/config.md#_snippet_4

LANGUAGE: python
CODE:
```
from agents import set_tracing_disabled

set_tracing_disabled(True)
```

----------------------------------------

TITLE: Create new inline snapshots
DESCRIPTION: Generates new inline snapshots for tests. This command is typically used when adding new snapshot tests to the project and needs to be run to establish the initial snapshot state.
SOURCE: https://github.com/openai/openai-agents-python/blob/main/tests/README.md#_snippet_2

LANGUAGE: Shell
CODE:
```
make snapshots-update
```

----------------------------------------

TITLE: Check uv Version
DESCRIPTION: Verifies the installed version of the `uv` package manager, which is a prerequisite for setting up the SDK development environment.
SOURCE: https://github.com/openai/openai-agents-python/blob/main/README.md#_snippet_6

LANGUAGE: bash
CODE:
```
uv --version
```

----------------------------------------

TITLE: Install OpenAI Agents Voice Dependencies
DESCRIPTION: Installs the necessary voice-related dependencies for the OpenAI Agents SDK using pip, enabling speech-to-text and text-to-speech functionalities.
SOURCE: https://github.com/openai/openai-agents-python/blob/main/docs/voice/quickstart.md#_snippet_0

LANGUAGE: bash
CODE:
```
pip install 'openai-agents[voice]'
```

----------------------------------------

TITLE: Generate Agent Graph with draw_graph Function
DESCRIPTION: Demonstrates how to define agents, tools, and handoffs, then use the `draw_graph` function to visualize their relationships. This creates a directed graph representing the agent structure, showing agents as yellow boxes, tools as green ellipses, and handoffs as directed edges.
SOURCE: https://github.com/openai/openai-agents-python/blob/main/docs/visualization.md#_snippet_1

LANGUAGE: python
CODE:
```
from agents import Agent, function_tool
from agents.extensions.visualization import draw_graph

@function_tool
def get_weather(city: str) -> str:
    return f"The weather in {city} is sunny."

spanish_agent = Agent(
    name="Spanish agent",
    instructions="You only speak Spanish.",
)

english_agent = Agent(
    name="English agent",
    instructions="You only speak English",
)

triage_agent = Agent(
    name="Triage agent",
    instructions="Handoff to the appropriate agent based on the language of the request.",
    handoffs=[spanish_agent, english_agent],
    tools=[get_weather],
)

draw_graph(triage_agent)
```

----------------------------------------

TITLE: Create Basic Agent Handoffs in Python
DESCRIPTION: Demonstrates how to create a simple agent handoff using the `Agent` and `handoff` functions. It shows how to assign other agents directly or via the `handoff()` function to an agent's `handoffs` parameter, enabling task delegation.
SOURCE: https://github.com/openai/openai-agents-python/blob/main/docs/ja/handoffs.md#_snippet_0

LANGUAGE: python
CODE:
```
from agents import Agent, handoff

billing_agent = Agent(name="Billing agent")
refund_agent = Agent(name="Refund agent")

triage_agent = Agent(name="Triage agent", handoffs=[billing_agent, handoff(refund_agent)])
```

----------------------------------------

TITLE: Save Agent Graph to a File
DESCRIPTION: Illustrates how to save the generated agent graph to a file (e.g., PNG) by specifying a `filename` argument to the `draw_graph` function. This creates an image file in the working directory, allowing for persistent storage and sharing of the visualization.
SOURCE: https://github.com/openai/openai-agents-python/blob/main/docs/visualization.md#_snippet_3

LANGUAGE: python
CODE:
```
draw_graph(triage_agent, filename="agent_graph")
```

----------------------------------------

TITLE: Install Agent Visualization Dependency
DESCRIPTION: Installs the optional 'viz' dependency group for the openai-agents library using pip. This enables the agent visualization features, including the `draw_graph` function, by installing necessary packages like Graphviz.
SOURCE: https://github.com/openai/openai-agents-python/blob/main/docs/visualization.md#_snippet_0

LANGUAGE: bash
CODE:
```
pip install "openai-agents[viz]"
```

----------------------------------------

TITLE: Run Streamed Voice Demo Application
DESCRIPTION: This command executes the main script for the streamed voice demo. It leverages Python's module execution feature to run the application directly from its package structure.
SOURCE: https://github.com/openai/openai-agents-python/blob/main/examples/voice/streamed/README.md#_snippet_0

LANGUAGE: python
CODE:
```
python -m examples.voice.streamed.main
```

----------------------------------------

TITLE: Run Multi-Agent Research Bot
DESCRIPTION: This command executes the main script for the multi-agent research bot. It initializes and runs the agent system, allowing it to perform web searches and generate reports based on user input.
SOURCE: https://github.com/openai/openai-agents-python/blob/main/examples/research_bot/README.md#_snippet_0

LANGUAGE: bash
CODE:
```
python -m examples.research_bot.main
```

----------------------------------------

TITLE: Add MCP servers to an Agent
DESCRIPTION: This Python snippet shows how to configure an `Agent` by assigning a list of initialized MCP server instances to its `mcp_servers` parameter. This allows the Agent to automatically discover and utilize tools provided by these MCP servers during its execution.
SOURCE: https://github.com/openai/openai-agents-python/blob/main/docs/ja/mcp.md#_snippet_1

LANGUAGE: python
CODE:
```
agent=Agent(
    name="Assistant",
    instructions="Use the tools to achieve the task",
    mcp_servers=[mcp_server_1, mcp_server_2]
)
```

----------------------------------------

TITLE: Install LiteLLM Dependency for OpenAI Agents SDK
DESCRIPTION: This command installs the LiteLLM dependency group for the OpenAI Agents SDK, enabling support for a wide range of non-OpenAI language models. It ensures that the necessary libraries are available for integrating models from various providers.
SOURCE: https://github.com/openai/openai-agents-python/blob/main/docs/models/index.md#_snippet_0

LANGUAGE: bash
CODE:
```
pip install "openai-agents[litellm]"
```

----------------------------------------

TITLE: Define Structured Inputs for Agent Handoffs in Python
DESCRIPTION: Shows how to define and use structured input data for agent handoffs using Pydantic `BaseModel`. This enables the LLM to provide specific, typed information when invoking a handoff, useful for logging or conditional logic within the `on_handoff` callback.
SOURCE: https://github.com/openai/openai-agents-python/blob/main/docs/handoffs.md#_snippet_2

LANGUAGE: python
CODE:
```
from pydantic import BaseModel

from agents import Agent, handoff, RunContextWrapper

class EscalationData(BaseModel):
    reason: str

async def on_handoff(ctx: RunContextWrapper[None], input_data: EscalationData):
    print(f"Escalation agent called with reason: {input_data.reason}")

agent = Agent(name="Escalation agent")

handoff_obj = handoff(
    agent=agent,
    on_handoff=on_handoff,
    input_type=EscalationData,
)
```

----------------------------------------

TITLE: Install LiteLLM dependency for OpenAI Agents
DESCRIPTION: This command installs the optional `litellm` dependency group for the `openai-agents` package. This step is crucial to enable the LiteLLM integration, providing access to a wide range of AI model providers.
SOURCE: https://github.com/openai/openai-agents-python/blob/main/docs/models/litellm.md#_snippet_0

LANGUAGE: bash
CODE:
```
pip install "openai-agents[litellm]"
```

----------------------------------------

TITLE: Define Handoff Input Data with Pydantic in Python
DESCRIPTION: Shows how to pass structured input data to a handoff using a Pydantic `BaseModel`. This allows the LLM to provide specific data (e.g., a reason for escalation) when invoking the handoff, which can then be processed by the `on_handoff` callback.
SOURCE: https://github.com/openai/openai-agents-python/blob/main/docs/ja/handoffs.md#_snippet_2

LANGUAGE: python
CODE:
```
from pydantic import BaseModel

from agents import Agent, handoff, RunContextWrapper

class EscalationData(BaseModel):
    reason: str

async def on_handoff(ctx: RunContextWrapper[None], input_data: EscalationData):
    print(f"Escalation agent called with reason: {input_data.reason}")

agent = Agent(name="Escalation agent")

handoff_obj = handoff(
    agent=agent,
    on_handoff=on_handoff,
    input_type=EscalationData,
)
```

----------------------------------------

TITLE: Implement Custom Guardrail for Agent Input/Output
DESCRIPTION: This code defines a custom guardrail using a Pydantic `BaseModel` for output validation. The `homework_guardrail` function runs a dedicated `guardrail_agent` to assess input data, returning a `GuardrailFunctionOutput` to indicate if a tripwire condition (e.g., not homework-related) is triggered.
SOURCE: https://github.com/openai/openai-agents-python/blob/main/docs/quickstart.md#_snippet_8

LANGUAGE: python
CODE:
```
from agents import GuardrailFunctionOutput, Agent, Runner
from pydantic import BaseModel

class HomeworkOutput(BaseModel):
    is_homework: bool
    reasoning: str

guardrail_agent = Agent(
    name="Guardrail check",
    instructions="Check if the user is asking about homework.",
    output_type=HomeworkOutput,
)

async def homework_guardrail(ctx, agent, input_data):
    result = await Runner.run(guardrail_agent, input_data, context=ctx.context)
    final_output = result.final_output_as(HomeworkOutput)
    return GuardrailFunctionOutput(
        output_info=final_output,
        tripwire_triggered=not final_output.is_homework,
    )
```

----------------------------------------

TITLE: Configure Agent Handoffs for Orchestration
DESCRIPTION: This snippet shows how to define handoff options for an agent. By assigning a list of other agents to the `handoffs` parameter, a `Triage Agent` can dynamically route tasks to appropriate specialist agents based on its instructions.
SOURCE: https://github.com/openai/openai-agents-python/blob/main/docs/quickstart.md#_snippet_6

LANGUAGE: python
CODE:
```
triage_agent = Agent(
    name="Triage Agent",
    instructions="You determine which agent to use based on the user's homework question",
    handoffs=[history_tutor_agent, math_tutor_agent]
)
```

----------------------------------------

TITLE: Customize Agent Handoff Behavior in Python
DESCRIPTION: Illustrates how to use the `handoff()` function to customize various aspects of an agent handoff, including `on_handoff` callbacks, `tool_name_override`, and `tool_description_override`. This allows for fine-grained control over handoff execution and LLM interaction.
SOURCE: https://github.com/openai/openai-agents-python/blob/main/docs/handoffs.md#_snippet_1

LANGUAGE: python
CODE:
```
from agents import Agent, handoff, RunContextWrapper

def on_handoff(ctx: RunContextWrapper[None]):
    print("Handoff called")

agent = Agent(name="My agent")

handoff_obj = handoff(
    agent=agent,
    on_handoff=on_handoff,
    tool_name_override="custom_handoff_tool",
    tool_description_override="Custom description",
)
```

----------------------------------------

TITLE: Display Agent Graph in Separate Window
DESCRIPTION: Shows how to display the generated agent graph in a separate viewer window. By calling the `.view()` method on the graph object returned by `draw_graph`, the visualization is opened in a new window, typically using the default image viewer.
SOURCE: https://github.com/openai/openai-agents-python/blob/main/docs/visualization.md#_snippet_2

LANGUAGE: python
CODE:
```
draw_graph(triage_agent).view()
```

----------------------------------------

TITLE: Fix broken inline snapshots
DESCRIPTION: Updates or creates new inline snapshots for tests that have changed or are newly added. This command should be run after code modifications that affect snapshot tests to ensure they pass.
SOURCE: https://github.com/openai/openai-agents-python/blob/main/tests/README.md#_snippet_1

LANGUAGE: Shell
CODE:
```
make snapshots-fix
```

----------------------------------------

TITLE: Activate Python Virtual Environment
DESCRIPTION: This command activates the previously created Python virtual environment. It must be run in each new terminal session to ensure project dependencies are correctly used and to access installed packages.
SOURCE: https://github.com/openai/openai-agents-python/blob/main/docs/quickstart.md#_snippet_1

LANGUAGE: bash
CODE:
```
source .venv/bin/activate
```

----------------------------------------

TITLE: Disable Sensitive Data Logging via Environment Variables
DESCRIPTION: Instructions on how to prevent the logging of sensitive LLM input/output data and tool input/output data by setting specific environment variables.
SOURCE: https://github.com/openai/openai-agents-python/blob/main/docs/config.md#_snippet_7

LANGUAGE: bash
CODE:
```
export OPENAI_AGENTS_DONT_LOG_MODEL_DATA=1
```

LANGUAGE: bash
CODE:
```
export OPENAI_AGENTS_DONT_LOG_TOOL_DATA=1
```
