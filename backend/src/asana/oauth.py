# backend/src/asana/oauth.py

import httpx
from pydantic import BaseModel

from ..config import settings
from ..logging import logger
from .token_store import StoredToken, TokenStore

class AsanaTokenResponse(BaseModel):
    access_token: str
    expires_in: int
    token_type: str
    refresh_token: str

async def exchange_code_for_token(code: str) -> AsanaTokenResponse:
    token_url = "https://app.asana.com/-/oauth_token"
    payload = {
        "grant_type": "authorization_code",
        "client_id": settings.ASANA_CLIENT_ID,
        "client_secret": settings.ASANA_CLIENT_SECRET,
        "redirect_uri": settings.ASANA_REDIRECT_URI,
        "code": code,
    }
    async with httpx.AsyncClient() as client:
        resp = await client.post(token_url, data=payload)
    resp.raise_for_status()

    data = resp.json()
    return AsanaTokenResponse(**data)

async def handle_oauth_callback(code: str) -> AsanaTokenResponse:
    """
    Exchange code → token, then persist it.
    """
    token = await exchange_code_for_token(code)
    # Persist only the fields we care about
    store_model = StoredToken(
        access_token=token.access_token,
        refresh_token=token.refresh_token,
        expires_in=token.expires_in,
    )
    TokenStore.save(store_model)
    logger.info("Saved Asana OAuth tokens to disk")
    return token
