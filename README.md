# langchain-deepagents

Research agent built on `deepagents` 0.6.2 (May 2026). Tools live on a separate MCP server. An HTTP API sits in front.

## What's interesting here

- Real `deepagents` v1 — planning loop, virtual filesystem, sub-agents, persistent memory are first-class, not bolted on.
- Tools served over MCP in a child process. The agent connects via stdio. Swap the tools without touching the agent.
- FastAPI on top, so the agent is usable from anywhere that can POST JSON.

## Architecture

```
POST /invoke {task}
      │
      ▼
   FastAPI ── lifespan ──> build_agent()
      │                        │
      │                        ├─ create_deep_agent(model, tools, system_prompt)
      │                        │
      │                        └─ MultiServerMCPClient ──stdio──> mcp_server.py
      │                                                            ├─ arxiv_search
      │                                                            ├─ fetch_url
      │                                                            └─ save_note
      ▼
   {answer}
```

## Run

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # set ANTHROPIC_API_KEY or OPENAI_API_KEY + MODEL
```

One-shot CLI:

```bash
python cli.py "Find 3 May 2026 papers on agentic RAG and save a note"
```

HTTP API:

```bash
uvicorn api:app --port 8000
# in another shell:
curl -s -X POST localhost:8000/invoke \
  -H 'content-type: application/json' \
  -d '{"task":"Find 3 May 2026 papers on agentic RAG and save a note"}' | jq
```

Health check: `GET /health` returns `{"status":"ok","agent_ready":true}`.

## Layout

- `agent.py` — builds the deep agent and connects to the MCP child process
- `mcp_server.py` — FastMCP server, 3 research tools
- `api.py` — FastAPI app over the agent
- `cli.py` — one-shot CLI runner
- `legacy/` — old validation notebooks from before `deepagents` v1 shipped

## Notes

- `MODEL=anthropic:claude-sonnet-4-6` is the default; switch to `openai:gpt-5.4` (or anything supporting tool calling) without code changes.
- Notes saved by the agent land under `./notes/` (ignored by git).
- The MCP server runs as a child process spawned over stdio. To poke at it directly: `python mcp_server.py` and connect via MCP Inspector.

## Refs

- `deepagents` 0.6.2 — github.com/langchain-ai/deepagents
- Deep Agents launch (March 2026) — langchain.com/deep-agents
- Model Context Protocol — modelcontextprotocol.io
- `langchain-mcp-adapters` — github.com/langchain-ai/langchain-mcp-adapters
- `FastMCP` — github.com/jlowin/fastmcp
