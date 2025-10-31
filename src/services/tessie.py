"""Async Tessie proxy utilities."""
from __future__ import annotations

import json
import uuid
from typing import Any, Dict, Optional

import aiohttp

from src.d1.client import D1Client, log_row
from src.services.logging import log_event

BASE_URL = "https://api.tessie.com"


class TessieService:
    """HTTP proxy that authenticates against the Tessie API."""

    def __init__(self, env: Any):
        api_key = getattr(env, "TESSIE_API_KEY", None)
        if not api_key:
            raise RuntimeError("TESSIE_API_KEY secret missing")
        self.env = env
        self.api_key = api_key
        self.client = D1Client(env.DB)

    async def request(
        self,
        method: str,
        path: str,
        query: Optional[Dict[str, Any]] = None,
        body: Optional[Any] = None,
    ) -> Dict[str, Any]:
        url = f"{BASE_URL}/{path.lstrip('/')}"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        async with aiohttp.ClientSession() as session:
            async with session.request(method.upper(), url, params=query, json=body, headers=headers) as resp:
                data = await resp.json(content_type=None)
                await self._record_raw(path, data, resp.status)
                return {"status": resp.status, "data": data, "headers": dict(resp.headers)}

    async def fetch_vehicle_snapshot(self, vin: str) -> Dict[str, Any]:
        path = f"api/vehicles/{vin}"
        result = await self.request("GET", path)
        return result

    async def _record_raw(self, endpoint: str, payload: Any, status: int) -> None:
        record_id = str(uuid.uuid4())
        await log_row(
            self.env.DB,
            "tessie_raw",
            {
                "id": record_id,
                "vehicle_id": None,
                "endpoint": endpoint,
                "payload": json.dumps({"status": status, "payload": payload}),
            },
        )
        await log_event(
            self.env,
            "INFO",
            "tessie response captured",
            {"endpoint": endpoint, "status": status, "record_id": record_id},
        )


async def proxy_request(
    env: Any,
    vin: str,
    path: str,
    method: str,
    query: Optional[Dict[str, Any]],
    body: Optional[Any],
) -> Dict[str, Any]:
    service = TessieService(env)
    proxy_path = f"api/vehicles/{vin}/{path}" if path else f"api/vehicles/{vin}"
    return await service.request(method, proxy_path, query=query, body=body)
