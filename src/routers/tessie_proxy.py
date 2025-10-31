"""Proxy endpoints to the Tessie REST API."""
from __future__ import annotations

from typing import Any, Dict, Optional

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from src.services.tessie import proxy_request

router = APIRouter(prefix="/tessieapi", tags=["tessie"])


@router.api_route("/{vin}/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
async def tessie_proxy(vin: str, path: str, request: Request) -> JSONResponse:
    env = request.scope["env"]
    body: Optional[Any] = None
    if request.method in {"POST", "PUT", "PATCH"}:
        body = await request.json()
    result = await proxy_request(env, vin, path, request.method, dict(request.query_params), body)
    response = JSONResponse(content=result["data"], status_code=result["status"])
    for key, value in result["headers"].items():
        if key.lower().startswith("cf-"):
            continue
        response.headers[key] = value
    return response
