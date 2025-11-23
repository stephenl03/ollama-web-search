"""Web Search Tool for Ollama integration using SearXNG."""

import httpx
from homeassistant.core import HomeAssistant
from homeassistant.helpers.llm import Tool, ToolInput

from .const import CONF_SEARXNG_URL, DEFAULT_SEARXNG_URL, DOMAIN


class WebSearchTool(Tool):
    name = "web_search"
    description = "Search the web using SearXNG and return the top results."
    parameters = {
        "query": {
            "type": "string",
            "description": "Search query to look up on the web."
        }
    }

    def __init__(self, hass: HomeAssistant) -> None:
        """Initialize the tool."""
        self.hass = hass

    async def call(self, tool_input: ToolInput) -> str:
        query = tool_input.args.get("query")
        if not query:
            return "No query provided."

        # Get SearXNG URL from config entries
        searxng_url = DEFAULT_SEARXNG_URL
        for entry in self.hass.config_entries.async_entries(DOMAIN):
            if CONF_SEARXNG_URL in entry.data:
                searxng_url = entry.data[CONF_SEARXNG_URL]
                break

        params = {
            "q": query,
            "format": "json",
            "categories": "general"
        }
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(searxng_url, params=params, timeout=10)
                response.raise_for_status()
                data = response.json()
                results = data.get("results", [])
                if not results:
                    return "No results found."
                # Return top 3 results as a summary
                summary = "\n".join([
                    f"{r.get('title')}: {r.get('url')}\n{r.get('content','')}"
                    for r in results[:3]
                ])
                return summary
            except Exception as e:
                return f"Web search failed: {e}"
