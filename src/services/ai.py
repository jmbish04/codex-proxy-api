"""Workers AI helper utilities."""
from __future__ import annotations

from typing import Any, AsyncGenerator, Dict


async def run_chat(env: Any, model: str, prompt: str) -> Dict[str, Any]:
    ai = getattr(env, "WORKERS_AI", None)
    if ai is None:
        raise RuntimeError("WORKERS_AI binding is not configured")
    return await ai.run(model, {"prompt": prompt})


async def stream_chat(env: Any, model: str, prompt: str) -> AsyncGenerator[str, None]:
    ai = getattr(env, "WORKERS_AI", None)
    if ai is None:
        raise RuntimeError("WORKERS_AI binding is not configured")
    stream = await ai.run(model, {"prompt": prompt, "stream": True})
    async for chunk in stream:
        yield chunk
