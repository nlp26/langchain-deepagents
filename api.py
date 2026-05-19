"""FastAPI front for the deep agent. POST /invoke {task} -> {answer}."""
from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from pydantic import BaseModel

from agent import build_agent

_state: dict = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    _state["agent"] = await build_agent()
    yield
    _state.clear()


app = FastAPI(title="langchain-deepagents", lifespan=lifespan)


class TaskIn(BaseModel):
    task: str


class TaskOut(BaseModel):
    answer: str


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "agent_ready": "agent" in _state}


@app.post("/invoke", response_model=TaskOut)
async def invoke(payload: TaskIn) -> TaskOut:
    agent = _state["agent"]
    result = await agent.ainvoke({"messages": [{"role": "user", "content": payload.task}]})
    msgs = result.get("messages") or []
    answer = ""
    if msgs:
        last = msgs[-1]
        answer = getattr(last, "content", None) or str(last)
    return TaskOut(answer=answer)
