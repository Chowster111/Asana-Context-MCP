import pytest
import httpx
from asana.oauth import refresh_access_token

@pytest.mark.asyncio
async def test_refresh_token_exchange(monkeypatch):
    # mock httpx AsyncClient
    class DummyResponse:
        status_code = 200
        def raise_for_status(self): pass
        def json(self): return {
            "access_token": "new_at",
            "refresh_token": "new_rt",
            "expires_in": 3600,
            "token_type": "Bearer"
        }

    class DummyClient:
        async def __aenter__(self): return self
        async def __aexit__(self, exc_type, exc, tb): pass
        async def post(self, url, data): return DummyResponse()

    monkeypatch.setattr(httpx, 'AsyncClient', lambda: DummyClient())

    result = await refresh_access_token("old_rt")
    assert result.access_token == "new_at"
    assert result.refresh_token == "new_rt"
    assert result.expires_in == 3600
