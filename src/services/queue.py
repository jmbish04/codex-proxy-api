"""Queue helpers for background work."""
from __future__ import annotations

import json
from typing import Any

from src.services.logging import log_event


async def enqueue_action(env: Any, payload: dict[str, Any]) -> None:
    queue = getattr(env, "CORE_TESSIE_QUEUE", None)
    if queue is None:
        raise RuntimeError("Queue binding CORE_TESSIE_QUEUE not configured")
    await queue.send(json.dumps(payload))


async def handle_queue_message(message: Any, env: Any) -> None:
    await log_event(env, "INFO", "Queue message processed", {"message_id": message.id})
