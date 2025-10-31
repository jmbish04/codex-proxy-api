"""Request logging utilities writing into the D1 logs table."""
from __future__ import annotations

import json
import uuid
from typing import Any

from src.d1.client import log_row


async def log_request(request: Any, response: Any, env: Any) -> None:
    """Persist a verbose record of the request/response pair."""

    method = getattr(request, "method", "GET")
    url = str(getattr(request, "url", ""))
    headers = dict(getattr(request, "headers", {}))
    status = getattr(response, "status", None) or getattr(response, "status_code", 0)
    response_headers = dict(getattr(response, "headers", {}))

    payload = {
        "id": str(uuid.uuid4()),
        "route": getattr(request, "url", getattr(request, "path", "")),
        "actor": headers.get("cf-connecting-ip"),
        "request_id": headers.get("cf-ray"),
        "level": "INFO" if status and status < 500 else "ERROR",
        "message": f"{method} {url}",
        "payload": json.dumps(
            {
                "request": {"method": method, "headers": headers},
                "response": {"status": status, "headers": response_headers},
            }
        ),
    }
    await log_row(env.DB, "logs", payload)


async def log_event(env: Any, level: str, message: str, extra: dict[str, Any] | None = None) -> None:
    payload = {
        "id": str(uuid.uuid4()),
        "route": "cron",
        "actor": "system",
        "request_id": None,
        "level": level,
        "message": message,
        "payload": json.dumps(extra or {}),
    }
    await log_row(env.DB, "logs", payload)
