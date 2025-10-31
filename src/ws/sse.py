"""Server-Sent Events fallback for agent streams."""
from __future__ import annotations

from typing import AsyncGenerator

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

router = APIRouter()


@router.get("/events")
async def events() -> StreamingResponse:
    async def generator() -> AsyncGenerator[bytes, None]:
        yield b"data: ready\n\n"
    return StreamingResponse(generator(), media_type="text/event-stream")
