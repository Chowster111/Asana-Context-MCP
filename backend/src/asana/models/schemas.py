# backend/src/asana/schemas.py

from pydantic import BaseModel
from typing import List, Dict, Any, Optional

class AttachContextRequest(BaseModel):
    """
    Payload for attaching a named MCP context to an Asana task.
    """
    task_gid: str
    context_name: str

class AsanaEvent(BaseModel):
    """
    A single event delivered via Asana webhook.
    You can expand these fields as needed.
    """
    resource: Dict[str, Any]
    action: str
    user: Dict[str, Any]
    created_at: str
    parent: Optional[Dict[str, Any]]

class AsanaWebhookPayload(BaseModel):
    """
    The full webhook payload from Asana.
    """
    events: List[AsanaEvent]
    # You can add `workspace`, `organization`, etc., as needed.
