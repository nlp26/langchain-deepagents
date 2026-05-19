"""One-shot CLI: python cli.py "research the latest in agentic RAG and save a note"."""
from __future__ import annotations

import asyncio
import sys

from agent import build_agent


async def _run(task: str) -> str:
    agent = await build_agent()
    result = await agent.ainvoke({"messages": [{"role": "user", "content": task}]})
    msgs = result.get("messages") or []
    if not msgs:
        return ""
    last = msgs[-1]
    return getattr(last, "content", None) or str(last)


def main() -> int:
    task = " ".join(sys.argv[1:]).strip() or "Find 3 May 2026 papers on agentic RAG and save a note."
    print(asyncio.run(_run(task)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
