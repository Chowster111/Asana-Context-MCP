# backend/src/mcp_client.py

import httpx
from pydantic import BaseModel
from typing import Any, Dict

from config import settings
from logging import logger

class MCPError(Exception):
    pass

class MCPClient:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")

    async def fetch_context(self, name: str) -> str:
        url = f"{self.base_url}/contexts/{name}"
        async with httpx.AsyncClient() as client:
            resp = await client.get(url)
        try:
            resp.raise_for_status()
        except httpx.HTTPStatusError as e:
            logger.error("Failed to fetch context '%s' from MCP: %s %s", name, resp.status_code, resp.text)
            raise MCPError(f"MCP fetch failed: {resp.status_code}") from e
        payload = resp.json()
        # assume MCP returns {"context_text": "..."}
        return payload.get("context_text", "")
