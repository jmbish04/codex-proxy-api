"""FastAPI application factory registering all routers."""
from __future__ import annotations

from fastapi import FastAPI, Request

from src.config import get_settings
from src.routers import agent_ops, colby_commands, d1_ops, openapi, tessie_proxy
from src.services.cors import apply_cors, preflight_response
from src.ws import sse, websocket


def create_app() -> FastAPI:
    app = FastAPI(title="Core Tessie API", version="0.1.0")

    @app.middleware("http")
    async def cors_middleware(request: Request, call_next):  # type: ignore[override]
        env = request.scope.get("env")
        settings = get_settings(env) if env else None
        if request.method == "OPTIONS" and settings:
            return preflight_response(request, settings.cors_allowed_origins)
        response = await call_next(request)
        if settings:
            apply_cors(response, settings.cors_allowed_origins, request.headers.get("origin"))
        return response

    app.include_router(openapi.router)
    app.include_router(d1_ops.router)
    app.include_router(tessie_proxy.router)
    app.include_router(colby_commands.router)
    app.include_router(agent_ops.router)
    app.include_router(websocket.router)
    app.include_router(sse.router)

    return app
