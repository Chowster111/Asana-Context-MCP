# backend/src/asana/token_store.py

import json
from pathlib import Path
from threading import Lock
from typing import Optional
from datetime import datetime, timedelta

from pydantic import BaseModel

from .oauth import refresh_access_token  # import your refresh helper

_TOKEN_FILE = Path(__file__).parent / "asana_tokens.json"
_lock = Lock()

class StoredToken(BaseModel):
    access_token: str
    refresh_token: str
    expires_in: int                # seconds until expiry
    issued_at: datetime            # when this token was issued

    @property
    def is_expired(self) -> bool:
        return datetime.utcnow() >= self.issued_at + timedelta(seconds=self.expires_in)

class TokenStore:

    @staticmethod
    def save(token: StoredToken) -> None:
        data = {
            **token.dict(),
            "issued_at": token.issued_at.isoformat()
        }
        with _lock:
            tmp = _TOKEN_FILE.with_suffix(".tmp")
            tmp.write_text(json.dumps(data, indent=2))
            tmp.replace(_TOKEN_FILE)

    @staticmethod
    def load() -> Optional[StoredToken]:
        if not _TOKEN_FILE.exists():
            return None

        raw = json.loads(_TOKEN_FILE.read_text())
        raw["issued_at"] = datetime.fromisoformat(raw["issued_at"])
        token = StoredToken(**raw)

        if token.is_expired:
            # automatically refresh
            refreshed = refresh_access_token(token.refresh_token)
            new_token = StoredToken(
                access_token=refreshed.access_token,
                refresh_token=refreshed.refresh_token,
                expires_in=refreshed.expires_in,
                issued_at=datetime.utcnow()
            )
            TokenStore.save(new_token)
            return new_token

        return token
