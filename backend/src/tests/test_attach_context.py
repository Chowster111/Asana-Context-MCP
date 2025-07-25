# tests/test_attach_context.py

import pytest
from httpx import AsyncClient
from fastapi import status

from backend.src.main import app
from asana.token_store import TokenStore, StoredToken
from datetime import datetime, timedelta

@pytest.fixture(autouse=True)
def setup_token(tmp_path, monkeypatch):
    # Point token store at tmp file
    tok = StoredToken(
        access_token="valid_at",
        refresh_token="rt",
        expires_in=3600,
        issued_at=datetime.utcnow()
    )
    file = tmp_path / "asana_tokens.json"
    file.write_text(tok.json())
    monkeypatch.setattr("asana.token_store._TOKEN_FILE", file)
    yield

@pytest.mark.asyncio
async def test_attach_context_success(monkeypatch):
    # Mock MCP fetch
    async def fake_fetch(name):
        return "Hello from MCP"
    monkeypatch.setattr("mcp_client.MCPClient.fetch_context", fake_fetch)

    # Mock Asana POST
    class DummyResp:
        status_code = 201
        text = ""
    async def fake_post(self, url, json, headers):
        return DummyResp()
    monkeypatch.setattr("httpx.AsyncClient.post", fake_post)

    async with AsyncClient(app=app, base_url="http://test") as ac:
        resp = await ac.post("/asana/attach-context", json={
            "task_gid": "12345",
            "context_name": "foo"
        })
    assert resp.status_code == status.HTTP_204_NO_CONTENT

@pytest.mark.asyncio
async def test_attach_context_mcp_fail(monkeypatch):
    async def fake_fetch(name):
        raise Exception("not found")
    monkeypatch.setattr("mcp_client.MCPClient.fetch_context", fake_fetch)

    async with AsyncClient(app=app, base_url="http://test") as ac:
        resp = await ac.post("/asana/attach-context", json={
            "task_gid": "12345",
            "context_name": "foo"
        })
    assert resp.status_code == status.HTTP_502_BAD_GATEWAY
