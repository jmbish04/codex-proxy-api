"""WorkerEntrypoint bridging FastAPI with Cloudflare Workers."""
from __future__ import annotations

import asgi
from js import Response, console
from workers import WorkerEntrypoint

from src.app import create_app
from src.services.logging import log_request
from src.services.queue import handle_queue_message
from src.services.sync import run_sync

app = create_app()


class Default(WorkerEntrypoint):
    """Entrypoint that proxies fetch events to the FastAPI ASGI app."""

    async def fetch(self, request, env):
        if request.headers.get("cf-cron"):
            console.log("Cron triggered: running sync")
            await run_sync(env)
            return Response.json({"status": "sync complete"})

        try:
            response = await asgi.fetch(app, request, env)
        except Exception as exc:  # pragma: no cover - defensive catch
            console.error(f"ASGI app error: {exc}")
            response = Response.json({"error": str(exc)}, status=500)

        try:
            await log_request(request, response, env)
        except Exception as log_exc:  # pragma: no cover - defensive catch
            console.error(f"Failed to log request: {log_exc}")

        return response

    async def queue(self, batch, env):
        for message in batch.messages:
            console.log(f"Queue message received: {message.id}")
            try:
                await handle_queue_message(message, env)
                message.ack()
            except Exception as e:
                console.error(f"Error processing queue message {message.id}: {e}")
