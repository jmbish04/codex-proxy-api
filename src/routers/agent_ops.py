"""Agent chat and action interfaces."""
from __future__ import annotations

import json
import uuid
from typing import Any, AsyncGenerator

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import StreamingResponse

from src.d1.client import D1Client
from src.services.ai import stream_chat
from src.services.queue import enqueue_action

router = APIRouter(prefix="/agent", tags=["agent"])


@router.post("/chat")
async def chat(request: Request):
    env = request.scope["env"]
    payload = await request.json()
    prompt = payload.get("prompt")
    if not prompt:
        raise HTTPException(status_code=400, detail="prompt is required")
    model = payload.get("model", "@cf/meta/llama-3-8b-instruct")
    message_id = str(uuid.uuid4())
    client = D1Client(env.DB)
    await client.execute(
        "INSERT INTO agent_messages (id, role, content, metadata) VALUES (?, ?, ?, ?)",
        message_id,
        "user",
        prompt,
        json.dumps({"model": model}),
    )

    async def token_stream() -> AsyncGenerator[bytes, None]:
        async for chunk in stream_chat(env, model, prompt):
            yield f"data: {chunk}\n\n".encode()
        yield b"data: [DONE]\n\n"

    return StreamingResponse(token_stream(), media_type="text/event-stream")


@router.post("/actions")
async def actions(request: Request):
    env = request.scope["env"]
    payload = await request.json()
    action_type = payload.get("type")
    if not action_type:
        raise HTTPException(status_code=400, detail="type is required")
    action_id = str(uuid.uuid4())
    client = D1Client(env.DB)
    await client.execute(
        "INSERT INTO agent_actions (id, type, payload, status) VALUES (?, ?, ?, ?)",
        action_id,
        action_type,
        json.dumps(payload),
        "queued",
    )
    await enqueue_action(env, {"id": action_id, "type": action_type, "payload": payload})
    return {"id": action_id, "status": "queued"}
