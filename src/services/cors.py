"""CORS helpers for FastAPI responses."""
from __future__ import annotations

from typing import Iterable

from fastapi import Request, Response


def apply_cors(response: Response, origins: Iterable[str], request_origin: str | None = None) -> None:
    origin = "*"
    normalized_origins = [o.strip() for o in origins if o]
    if request_origin and request_origin in normalized_origins:
        origin = request_origin
    elif normalized_origins:
        origin = ", ".join(normalized_origins)

    response.headers["Access-Control-Allow-Origin"] = origin
    response.headers["Access-Control-Allow-Methods"] = "GET,POST,PUT,PATCH,DELETE,OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Authorization,Content-Type"
    response.headers["Access-Control-Allow-Credentials"] = "true"


def preflight_response(request: Request, origins: Iterable[str]) -> Response:
    response = Response(status_code=204)
    apply_cors(response, origins, request.headers.get("origin"))
    response.headers["Access-Control-Max-Age"] = "86400"
    requested_headers = request.headers.get("Access-Control-Request-Headers", "")
    if requested_headers:
        response.headers["Access-Control-Allow-Headers"] = requested_headers
    return response
