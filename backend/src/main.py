# backend/src/main.py

import sys
import logging
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel, BaseSettings
import httpx

from asana.oauth import handle_oauth_callback, AsanaTokenResponse
from asana.schemas import AttachContextRequest
from asana.token_store import TokenStore, StoredToken
from mcp_client import MCPClient, MCPError

class Settings(BaseSettings):
    MCP_SERVER_URL: str
    ASANA_CLIENT_ID: str
    ASANA_CLIENT_SECRET: str
    ASANA_REDIRECT_URI: str

    class Config:
        env_file = ".env"
        env_prefix = ""

settings = Settings()
mcp_client = MCPClient(settings.MCP_SERVER_URL)

logger = logging.getLogger("mcp_asana")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(logging.Formatter("[%(asctime)s] %(levelname)s %(name)s: %(message)s"))
logger.addHandler(handler)

app = FastAPI(title="MCP ↔ Asana Context-Linker", version="0.1.0")

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled exception: %s", exc)
    if isinstance(exc, HTTPException):
        return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})
    return JSONResponse(status_code=500, content={"detail": "Internal Server Error"})

class HealthCheckResponse(BaseModel):
    status: str = "ok"
    mcp_server: str

@app.get("/health", response_model=HealthCheckResponse)
async def health_check():
    logger.info("Health check requested")
    return HealthCheckResponse(mcp_server=settings.MCP_SERVER_URL)

@app.get("/asana/oauth/callback", response_model=AsanaTokenResponse, summary="Handle Asana OAuth redirect")
async def asana_oauth_callback(code: str):
    logger.info("Received OAuth callback, exchanging code")
    try:
        token = await handle_oauth_callback(code)
    except Exception:
        raise HTTPException(status_code=502, detail="Failed to exchange or save OAuth token")
    return token

@app.post("/asana/attach-context", status_code=204, summary="Attach a named MCP context to an Asana task")
async def attach_context(payload: AttachContextRequest):
    logger.info("attach-context called with payload: %s", payload.json())

    # Load token
    token: StoredToken = TokenStore.load()
    if not token:
        logger.error("No Asana token found; re-auth required")
        raise HTTPException(status_code=401, detail="Missing Asana credentials")

    # Fetch context from MCP
    try:
        context_text = await mcp_client.fetch_context(payload.context_name)
    except MCPError as e:
        raise HTTPException(status_code=502, detail=str(e))

    # Post to Asana
    url = f"https://app.asana.com/api/1.0/tasks/{payload.task_gid}/stories"
    headers = {"Authorization": f"Bearer {token.access_token}"}
    body = {"text": context_text}

    async with httpx.AsyncClient() as client:
        resp = await client.post(url, json=body, headers=headers)
    if resp.status_code >= 400:
        logger.error("Asana Stories API failed: %s %s", resp.status_code, resp.text)
        raise HTTPException(status_code=resp.status_code, detail="Failed to post to Asana")

    return JSONResponse(status_code=204)
