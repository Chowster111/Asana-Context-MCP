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
    """
    Exchange the OAuth `code` from Asana for an access + refresh token pair.
    """
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
    try:
        resp.raise_for_status()
    except httpx.HTTPStatusError as e:
        logger.error("OAuth token exchange failed: %s → %s", resp.status_code, resp.text)
        raise

    data = resp.json()
    return AsanaTokenResponse(**data)
