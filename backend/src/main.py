# backend/src/main.py

import sys
import logging
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel, BaseSettings

from asana.oauth import handle_oauth_callback, AsanaTokenResponse
from asana.schemas import AttachContextRequest

class Settings(BaseSettings):
    MCP_SERVER_URL: str
    ASANA_CLIENT_ID: str
    ASANA_CLIENT_SECRET: str
    ASANA_REDIRECT_URI: str

    class Config:
        env_file = ".env"
        env_prefix = ""

settings = Settings()

logger = logging.getLogger("mcp_asana")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(logging.Formatter("[%(asctime)s] %(levelname)s %(name)s: %(message)s"))
logger.addHandler(handler)

app = FastAPI(
    title="MCP ↔ Asana Context-Linker",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

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

@app.get(
    "/asana/oauth/callback",
    response_model=AsanaTokenResponse,
    summary="Handle Asana OAuth redirect"
)
async def asana_oauth_callback(code: str):
    logger.info("Received OAuth callback, exchanging code")
    try:
        token = await handle_oauth_callback(code)
    except Exception:
        raise HTTPException(status_code=502, detail="Failed to exchange or save OAuth token")
    return token

@app.post(
    "/asana/attach-context",
    status_code=204,
    summary="Attach a named MCP context to an Asana task"
)
async def attach_context(payload: AttachContextRequest):
    logger.info("attach-context called with payload: %s", payload.json())
    # TODO: implement MCP fetch and Asana post logic
    return JSONResponse(status_code=204)
