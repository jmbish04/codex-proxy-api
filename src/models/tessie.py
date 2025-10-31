"""DTOs for Tessie API payloads."""
from __future__ import annotations

from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class TessieRequest(BaseModel):
    method: str = Field(..., description="HTTP method")
    path: str = Field(..., description="Endpoint path")
    query: Optional[Dict[str, Any]] = None
    body: Optional[Any] = None


class TessieResponse(BaseModel):
    status: int
    headers: Dict[str, str]
    data: Any
