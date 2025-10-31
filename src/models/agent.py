"""Agent message and action schemas."""
from __future__ import annotations

from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class AgentMessage(BaseModel):
    id: str
    role: str = Field(..., description="speaker role")
    content: str = Field(..., description="message content")
    created_at: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class AgentAction(BaseModel):
    id: str
    type: str
    payload: Dict[str, Any]
    created_at: Optional[str] = None
    status: Optional[str] = None
