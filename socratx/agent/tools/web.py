"""Web tools: search and fetch."""

from typing import Any

from .base import Tool


class WebSearchTool(Tool):
    """Tool to search the web using Brave Search API."""

    name = "web_search"
    description = "Search the web for a query and return top results."
    parameters = {
        "type": "object",
        "properties": {
            "query": {"type": "string", "description": "Search query"},
            "count": {"type": "integer", "description": "Number of results", "default": 5, "maximum": 20},
        },
        "required": ["query"]
    }

    def __init__(self, api_key: str | None = None, count: int = 5):
        self.api_key = api_key
        self.count = count

    async def execute(self, query: str, count: int | None = None, **kwargs: Any) -> str:
        try:
            import requests
            count = count or self.count
            api_key = self.api_key
            
            if not api_key:
                return "Error: Brave API key not configured"

            url = "https://api.search.brave.com/res/v1/web/search"
            headers = {
                "Accept": "application/json",
                "X-Subscription-Token": api_key
            }
            params = {"q": query, "count": count}

            resp = requests.get(url, headers=headers, params=params, timeout=10)
            resp.raise_for_status()
            data = resp.json()

            results = []
            for r in data.get("web", {}).get("results", [])[:count]:
                results.append(f"- {r.get('title', '')}: {r.get('description', '')}")

            return "\n".join(results) if results else "No results found."

        except Exception as e:
            return f"Error searching web: {str(e)}"


class WebFetchTool(Tool):
    """Fetch and extract content from a URL using Readability."""

    name = "web_fetch"
    description = "Fetch URL and extract readable content (HTML/markdown/text)."
    parameters = {
        "type": "object",
        "properties": {
            "url": {"type": "string", "description": "URL to fetch"},
            "extractMode": {"type": "string", "enum": ["markdown", "text"], "default": "markdown"},
            "maxChars": {"type": "integer", "minimum": 100}
        },
        "required": ["url"]
    }

    def __init__(self, max_chars: int = 50000):
        self.max_chars = max_chars

    async def execute(self, url: str, extractMode: str = "markdown", maxChars: int | None = None, **kwargs: Any) -> str:
        try:
            import requests
            from readability import Document as ReadabilityDocument

            max_chars = maxChars or self.max_chars

            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
            resp = requests.get(url, headers=headers, timeout=10)
            resp.raise_for_status()

            doc = ReadabilityDocument(resp.text)
            content = doc.summary() if extractMode == "text" else doc.summary()

            return content[:max_chars]

        except Exception as e:
            return f"Error fetching URL: {str(e)}"
