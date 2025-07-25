# backend/src/asana/oauth.py

import httpx
from pydantic import BaseModel

from ..config import settings
from ..logging import logger

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
    return AsanaTokenResponse(**resp.json())

async def refresh_access_token(refresh_token: str) -> AsanaTokenResponse:
    """
    Use the Asana refresh_token to get a new access + refresh pair.
    """
    token_url = "https://app.asana.com/-/oauth_token"
    payload = {
        "grant_type": "refresh_token",
        "client_id": settings.ASANA_CLIENT_ID,
        "client_secret": settings.ASANA_CLIENT_SECRET,
        "refresh_token": refresh_token,
    }
    async with httpx.AsyncClient() as client:
        resp = await client.post(token_url, data=payload)
        try:
            resp.raise_for_status()
        except httpx.HTTPStatusError:
            logger.error("Refresh token exchange failed: %s → %s", resp.status_code, resp.text)
            raise
    logger.info("Successfully refreshed access token")
    return AsanaTokenResponse(**resp.json())

async def handle_oauth_callback(code: str) -> AsanaTokenResponse:
    token = await exchange_code_for_token(code)
    # persisted elsewhere using TokenStore.save()
    return token
