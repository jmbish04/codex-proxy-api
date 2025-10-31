"""Scheduled Tessie synchronization routines."""
from __future__ import annotations

import json
import uuid
from typing import Any, Dict

from src.d1.client import D1Client
from src.services.logging import log_event
from src.services.tessie import TessieService


async def run_sync(env: Any) -> None:
    """Entry point for the cron-triggered synchronization job."""

    client = D1Client(env.DB)
    sync_id = str(uuid.uuid4())
    await client.execute(
        "INSERT INTO sync_runs (id, status, started_at) VALUES (?, ?, CURRENT_TIMESTAMP)",
        sync_id,
        "running",
    )
    await log_event(env, "INFO", "Sync started", {"sync_id": sync_id})
    try:
        vehicles = await client.fetch_all("SELECT id, vin FROM vehicles")
        service = TessieService(env)
        for vehicle in vehicles:
            vin = vehicle.get("vin") or vehicle.get("id")
            if not vin:
                continue
            snapshot = await service.fetch_vehicle_snapshot(vin)
            await persist_snapshot(client, vehicle.get("id"), snapshot)
        await client.execute(
            "UPDATE sync_runs SET status = ?, finished_at = CURRENT_TIMESTAMP WHERE id = ?",
            "succeeded",
            sync_id,
        )
        await log_event(env, "INFO", "Sync completed", {"sync_id": sync_id, "vehicles": len(vehicles)})
    except Exception as exc:  # pragma: no cover - defensive catch
        await client.execute(
            "UPDATE sync_runs SET status = ?, finished_at = CURRENT_TIMESTAMP WHERE id = ?",
            "failed",
            sync_id,
        )
        await log_event(env, "ERROR", "Sync failed", {"sync_id": sync_id, "error": str(exc)})
        raise


async def persist_snapshot(client: D1Client, vehicle_id: str | None, snapshot: Dict[str, Any]) -> None:
    if not vehicle_id:
        return
    vehicle_data = snapshot.get("data", {})
    await client.execute(
        "UPDATE vehicles SET data = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
        json.dumps(vehicle_data),
        vehicle_id,
    )
