"""Deep agent assembled from deepagents 0.6.2 + MCP-served tools."""
from __future__ import annotations

import os
import sys
from pathlib import Path

from deepagents import create_deep_agent
from dotenv import load_dotenv
from langchain_mcp_adapters.client import MultiServerMCPClient

HERE = Path(__file__).resolve().parent
load_dotenv(HERE / ".env")

SYSTEM_PROMPT = """You are a research agent.

Available tools (served over MCP): arxiv_search, fetch_url, save_note.

Workflow:
1. Plan the task as a short todo list before acting.
2. Use arxiv_search to find papers; prefer recent results.
3. Use fetch_url only when an abstract is not enough.
4. Use save_note to persist a structured summary (title, refs, takeaways).
5. End your reply with the saved note's path and a 5-line summary citing arXiv ids.

Be terse. Cite arXiv ids inline. Do not invent results.
"""


def _mcp_config() -> dict:
    return {
        "research": {
            "command": sys.executable,
            "args": [str(HERE / "mcp_server.py")],
            "transport": "stdio",
        }
    }


async def build_agent(model: str | None = None):
    """Spawn the MCP server, load tools, return a ready-to-invoke deep agent."""
    client = MultiServerMCPClient(_mcp_config())
    tools = await client.get_tools()
    model_id = model or os.getenv("MODEL", "anthropic:claude-sonnet-4-6")
    return create_deep_agent(
        model=model_id,
        tools=tools,
        system_prompt=SYSTEM_PROMPT,
    )
