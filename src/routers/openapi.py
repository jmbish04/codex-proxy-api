"""OpenAPI document endpoints."""
from __future__ import annotations

import yaml
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse, PlainTextResponse

router = APIRouter(tags=["openapi"])


@router.get("/openapi.json")
async def openapi_json(request: Request) -> JSONResponse:
    schema = request.app.openapi()
    return JSONResponse(schema)


@router.get("/openapi.yaml")
async def openapi_yaml(request: Request) -> PlainTextResponse:
    schema = request.app.openapi()
    return PlainTextResponse(yaml.safe_dump(schema), media_type="application/yaml")
