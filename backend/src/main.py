# backend/src/main.py

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse

from .asana.oauth import exchange_code_for_token, AsanaTokenResponse
from .asana.schemas import AttachContextRequest
from .logging import logger


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
handler.setFormatter(
    logging.Formatter("[%(asctime)s] %(levelname)s %(name)s: %(message)s")
)
logger.addHandler(handler)

class HealthCheckResponse(BaseModel):
    status: str = "ok"
    mcp_server: str

app = FastAPI(
    title="MCP ↔ Asana Context-Linker",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled exception: %s", exc)
    # If it's an HTTPException, respect its status code
    if isinstance(exc, HTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail},
        )
    # Otherwise, return 500
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal Server Error"},
    )


@app.get("/health", response_model=HealthCheckResponse)
async def health_check():
    """
    Simple health check endpoint.
    Verifies the server is running and can reach the MCP server URL.
    """
    # (In a later iteration you might actually ping settings.MCP_SERVER_URL here.)
    logger.info("Health check requested")
    return HealthCheckResponse(mcp_server=settings.MCP_SERVER_URL)


@app.get(
    "/asana/oauth/callback",
    response_model=AsanaTokenResponse,
    summary="Handle Asana OAuth redirect"
)
async def asana_oauth_callback(code: str):
    """
    Exchange `code` for an Asana access token.
    """
    try:
        token = await exchange_code_for_token(code)
    except Exception as e:
        # exchange_code_for_token already logs the detail
        raise HTTPException(502, detail="Failed to exchange OAuth code")

    # TODO: persist `token.access_token` & `token.refresh_token` securely
    logger.info("Obtained Asana tokens for code=%s", code)
    return token


@app.post(
    "/asana/attach-context",
    status_code=204,
    summary="Attach a named MCP context to an Asana task"
)
async def attach_context(payload: AttachContextRequest):
    """
    Given a task GID and a context name, fetch the context
    from MCP and post it as a comment on the Asana task.
    (Implementation to come.)
    """
    logger.info("attach-context called: %s", payload.json())
    # TODO:
    # 1. fetch context from MCP via your mcpClient
    # 2. POST to https://app.asana.com/api/1.0/tasks/{task_gid}/stories
    return JSONResponse(status_code=204)
