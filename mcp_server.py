"""Research tools served over MCP. Run standalone or spawned by the agent over stdio."""
from __future__ import annotations

import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

import httpx
from fastmcp import FastMCP

mcp = FastMCP("research-tools")

NOTES_DIR = Path("notes")
ARXIV_NS = {"atom": "http://www.w3.org/2005/Atom"}


@mcp.tool
def arxiv_search(query: str, max_results: int = 5) -> list[dict]:
    """Search arXiv. Returns up to max_results entries with id, title, summary, pdf_url."""
    url = (
        "http://export.arxiv.org/api/query"
        f"?search_query={urllib.parse.quote(query)}&max_results={max_results}"
    )
    with urllib.request.urlopen(url, timeout=20) as resp:
        data = resp.read()
    root = ET.fromstring(data)
    out: list[dict] = []
    for entry in root.findall("atom:entry", ARXIV_NS):
        title = (entry.findtext("atom:title", default="", namespaces=ARXIV_NS) or "").strip()
        summary = (entry.findtext("atom:summary", default="", namespaces=ARXIV_NS) or "").strip()
        arxiv_id = (entry.findtext("atom:id", default="", namespaces=ARXIV_NS) or "").split("/")[-1]
        pdf_url = next(
            (
                link.get("href")
                for link in entry.findall("atom:link", ARXIV_NS)
                if link.get("type") == "application/pdf"
            ),
            None,
        )
        out.append({
            "id": arxiv_id,
            "title": title,
            "summary": summary[:600],
            "pdf_url": pdf_url,
        })
    return out


@mcp.tool
def fetch_url(url: str, max_chars: int = 6000) -> str:
    """Fetch a URL and return text content, truncated to max_chars."""
    with httpx.Client(timeout=20, follow_redirects=True) as client:
        r = client.get(url)
        r.raise_for_status()
        return r.text[:max_chars]


@mcp.tool
def save_note(name: str, content: str) -> str:
    """Save content to notes/<name>.md and return the absolute path."""
    NOTES_DIR.mkdir(exist_ok=True)
    safe = "".join(c if c.isalnum() or c in "-_" else "_" for c in name)
    path = (NOTES_DIR / f"{safe}.md").resolve()
    path.write_text(content)
    return str(path)


if __name__ == "__main__":
    mcp.run()  # stdio transport by default
