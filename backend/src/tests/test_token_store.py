import pytest
import json
from pathlib import Path
from datetime import datetime, timedelta

import httpx
from asana.token_store import TokenStore, StoredToken
from asana.oauth import refresh_access_token

TOKEN_PATH = Path(__file__).parent.parent / "backend/src/asana/asana_tokens.json"

@pytest.fixture(autouse=True)
def cleanup_token_file(tmp_path, monkeypatch):
    # redirect token file to tmp
    monkeypatch.setattr(
        'asana.token_store._TOKEN_FILE',
        tmp_path / "tokens.json"
    )
    yield

@pytest.mark.asyncio
async def test_auto_refresh(monkeypatch):
    # write expired token
    expired = {
        "access_token": "old",
        "refresh_token": "r_old",
        "expires_in": 1,
        "issued_at": (datetime.utcnow() - timedelta(seconds=10)).isoformat()
    }
    TOKEN_PATH.write_text(json.dumps(expired))

    # mock the refresh call
    async def fake_refresh(rt):
        return refresh_response
    refresh_response = await refresh_access_token.__wrapped__(expired["refresh_token"])  # or define manually

    monkeypatch.setattr('asana.token_store.refresh_access_token', fake_refresh)

    token = TokenStore.load()
    assert token.access_token == refresh_response.access_token
    assert token.refresh_token == refresh_response.refresh_token
    assert not token.is_expired
