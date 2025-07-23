# backend/src/asana/token_store.py

import json
from pathlib import Path
from threading import Lock
from typing import Optional

from pydantic import BaseModel

_TOKEN_FILE = Path(__file__).parent / "asana_tokens.json"
_lock = Lock()

class StoredToken(BaseModel):
    access_token: str
    refresh_token: str
    expires_in: Optional[int] = None  # seconds until expiry, if provided

class TokenStore:
    @staticmethod
    def save(token: StoredToken) -> None:
        """
        Save the latest token to disk (atomically).
        """
        data = token.dict()
        # ensure thread-safe writes
        with _lock:
            tmp = _TOKEN_FILE.with_suffix(".tmp")
            tmp.write_text(json.dumps(data, indent=2))
            tmp.replace(_TOKEN_FILE)

    @staticmethod
    def load() -> Optional[StoredToken]:
        """
        Load the saved token, or None if not present.
        """
        if not _TOKEN_FILE.exists():
            return None
        try:
            data = json.loads(_TOKEN_FILE.read_text())
            return StoredToken(**data)
        except Exception:
            return None
