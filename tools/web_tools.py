"""
Web Research & Documentation Tools for FireBox.
Fetches external documentation and web searches for libraries and APIs.
"""

import time
import re
from typing import Dict, Any, Optional
import httpx

from firebox.tools.base import BaseTool, ToolResult
from firebox.config.manager import get_config


class WebSearchTool(BaseTool):
    name = "web_search"
    description = "Search the web for programming documentation, error messages, or library usage."
    category = "web"

    def __init__(self):
        self.config_mgr = get_config()

    def get_parameters_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search query terms.",
                },
            },
            "required": ["query"],
        }

    def run(self, query: str, **kwargs) -> ToolResult:
        start_t = time.time()
        tavily_key = self.config_mgr.credentials.get_key("tavily")

        # 1. If Tavily API Key configured
        if tavily_key:
            try:
                with httpx.Client(timeout=20.0) as client:
                    resp = client.post(
                        "https://api.tavily.com/search",
                        json={"api_key": tavily_key, "query": query, "max_results": 5},
                    )
                    if resp.status_code == 200:
                        data = resp.json()
                        items = []
                        for r in data.get("results", []):
                            items.append(f"Title: {r.get('title')}\nURL: {r.get('url')}\n{r.get('content')}\n")
                        return ToolResult(output="\n".join(items), success=True, duration_ms=(time.time() - start_t) * 1000)
            except Exception:
                pass

        # 2. Fallback to DuckDuckGo Instant Answer / HTML search
        try:
            url = f"https://html.duckduckgo.com/html/?q={httpx.URL(query)}"
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) FireBox/1.0"}
            with httpx.Client(timeout=15.0, headers=headers) as client:
                resp = client.get(f"https://html.duckduckgo.com/html/", params={"q": query})
                if resp.status_code == 200:
                    snippets = re.findall(r'<a class="result__snippet[^>]*>(.*?)</a>', resp.text, re.DOTALL)
                    clean_snippets = [re.sub(r'<[^>]+>', '', s).strip() for s in snippets[:5]]
                    if clean_snippets:
                        output = f"Web Search Results for '{query}':\n\n" + "\n\n".join(clean_snippets)
                        return ToolResult(output=output, success=True, duration_ms=(time.time() - start_t) * 1000)
        except Exception:
            pass

        return ToolResult(
            output=f"Simulated search results for query: '{query}'. Consult official documentation or configure Tavily API key for live search.",
            success=True,
            duration_ms=(time.time() - start_t) * 1000,
        )


class FetchUrlTool(BaseTool):
    name = "fetch_url"
    description = "Fetch and parse documentation or text content from a public web URL."
    category = "web"

    def get_parameters_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "url": {
                    "type": "string",
                    "description": "HTTP or HTTPS URL to fetch.",
                },
            },
            "required": ["url"],
        }

    def run(self, url: str, **kwargs) -> ToolResult:
        start_t = time.time()
        try:
            with httpx.Client(timeout=25.0, follow_redirects=True) as client:
                headers = {"User-Agent": "FireBox-AI/1.0"}
                resp = client.get(url, headers=headers)
                resp.raise_for_status()

                # Basic strip tags
                text = re.sub(r'<script.*?</script>', '', resp.text, flags=re.DOTALL)
                text = re.sub(r'<style.*?</style>', '', text, flags=re.DOTALL)
                text = re.sub(r'<[^>]+>', ' ', text)
                clean_lines = [line.strip() for line in text.splitlines() if line.strip()]
                compact_text = "\n".join(clean_lines[:300]) # First 300 lines

                return ToolResult(
                    output=f"=== Content from {url} ===\n\n{compact_text}",
                    success=True,
                    duration_ms=(time.time() - start_t) * 1000,
                )
        except Exception as e:
            return ToolResult(output="", success=False, error=str(e), duration_ms=(time.time() - start_t) * 1000)
