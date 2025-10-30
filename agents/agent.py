from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm
from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPServerParams
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from mcp import StdioServerParameters
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset
from . import prompts
from dotenv import load_dotenv
import os

load_dotenv()

JINA_API_KEY = os.getenv("JINA_API_KEY")


root_agent = LlmAgent(
    model=LiteLlm(model="ollama_chat/qwen3:8b"),
    name="ai_agent",
    description="A mcp agent that search web or get contents from website",
    instruction=prompts.INSTRUCTION,
    tools=[
        MCPToolset(
            connection_params=StdioConnectionParams(
                server_params=StdioServerParameters(
                    command="npx",
                    args=[
                        "-y",
                        "mcp-remote",
                        "https://mcp.jina.ai/sse",
                        "--header",
                        f"Authorization: Bearer {JINA_API_KEY}",
                    ],
                ),
            ),
            tool_filter=["read_url", "search_web"],
        ),
        MCPToolset(
            connection_params=StdioConnectionParams(
                server_params=StdioServerParameters(
                    command="npx",
                    args=[
                        "-y",
                        "chrome-devtools-mcp@latest",
                    ],
                ),
            ),
            tool_filter=[
                "new_page",
                "navigate_page",
                "close_page",
                "list_pages",
                "select_page",
                "take_screenshot",
            ],
        ),
    ],
)
