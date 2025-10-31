"""CRUD endpoints for D1 tables."""
from __future__ import annotations

from typing import Any, Dict, List

from fastapi import APIRouter, HTTPException, Query, Request

from src.d1.client import D1Client
from src.d1 import queries
from src.models.agent import AgentAction, AgentMessage
from src.models.log import EnergyReport, LogRow, SyncRun, TessieRaw
from src.models.vehicle import (
    Charge,
    Climate,
    Drive,
    SoftwareUpdate,
    Vehicle,
    VehicleSettings,
)

router = APIRouter(prefix="/d1", tags=["d1"])


TABLE_CONFIG: Dict[str, Dict[str, Any]] = {
    "vehicles": {"model": Vehicle, "columns": ["id", "vin", "display_name", "data"]},
    "vehicle_settings": {"model": VehicleSettings, "columns": ["id", "vehicle_id", "data"]},
    "charges": {
        "model": Charge,
        "columns": ["id", "vehicle_id", "battery_level", "charge_energy_added"],
    },
    "drives": {
        "model": Drive,
        "columns": ["id", "vehicle_id", "distance_miles", "duration_seconds"],
    },
    "climates": {
        "model": Climate,
        "columns": ["id", "vehicle_id", "inside_temp_c", "outside_temp_c"],
    },
    "software_updates": {"model": SoftwareUpdate, "columns": ["id", "vehicle_id", "version", "status"]},
    "tessie_raw": {"model": TessieRaw, "columns": ["id", "vehicle_id", "endpoint", "payload"]},
    "sync_runs": {"model": SyncRun, "columns": ["id", "status", "started_at", "finished_at"]},
    "energy_reports": {
        "model": EnergyReport,
        "columns": ["id", "vehicle_id", "total_energy_added", "average_energy_added", "samples"],
    },
    "logs": {
        "model": LogRow,
        "columns": ["id", "route", "actor", "request_id", "level", "message", "payload"],
    },
    "agent_messages": {
        "model": AgentMessage,
        "columns": ["id", "role", "content", "metadata"],
    },
    "agent_actions": {
        "model": AgentAction,
        "columns": ["id", "type", "payload", "status"],
    },
}


def get_table_config(table: str) -> Dict[str, Any]:
    if table not in TABLE_CONFIG:
        raise HTTPException(status_code=404, detail=f"Unknown table: {table}")
    return TABLE_CONFIG[table]


@router.get("/{table}/list")
async def list_rows(
    table: str,
    request: Request,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    sort: str | None = None,
    order: str = Query("desc", regex="^(?i)(asc|desc)$"),
):
    env = request.scope["env"]
    client = D1Client(env.DB)
    config = get_table_config(table)
    sql = queries.select_base(table)
    filters: List[str] = []
    params: List[Any] = []
    for key, value in request.query_params.items():
        if key in {"limit", "offset", "sort", "order"}:
            continue
        if key not in config["columns"]:
            continue
        filters.append(f"{key} = ?")
        params.append(value)
    if filters:
        sql += " WHERE " + " AND ".join(filters)
    if sort and sort in config["columns"]:
        direction = "ASC" if order.lower() == "asc" else "DESC"
        sql += f" ORDER BY {sort} {direction}"
    sql += " LIMIT ? OFFSET ?"
    params.extend([limit, offset])
    rows = await client.fetch_all(sql, *params)
    return {"items": rows, "count": len(rows)}


@router.get("/{table}/{item_id}")
async def get_row(table: str, item_id: str, request: Request):
    env = request.scope["env"]
    client = D1Client(env.DB)
    get_table_config(table)
    row = await client.fetch_one(queries.select_by_id(table), item_id)
    if not row:
        raise HTTPException(status_code=404, detail="Record not found")
    return row


@router.post("/{table}")
async def create_row(table: str, request: Request):
    env = request.scope["env"]
    client = D1Client(env.DB)
    config = get_table_config(table)
    payload = await request.json()
    model = config["model"](**payload)
    data = model.dict(exclude_none=True)
    columns = {key: value for key, value in data.items() if key in config["columns"]}
    sql = queries.insert_base(table, columns)
    await client.execute(sql, *columns.values())
    return {"id": data["id"], "status": "created"}


@router.patch("/{table}/{item_id}")
async def update_row(table: str, item_id: str, request: Request):
    env = request.scope["env"]
    client = D1Client(env.DB)
    config = get_table_config(table)
    payload = await request.json()
    data = {key: value for key, value in payload.items() if key in config["columns"] and key != "id"}
    if not data:
        raise HTTPException(status_code=400, detail="No mutable columns provided")
    sql = queries.update_base(table, data)
    params = list(data.values()) + [item_id]
    await client.execute(sql, *params)
    return {"id": item_id, "status": "updated"}


@router.delete("/{table}/{item_id}")
async def delete_row(table: str, item_id: str, request: Request):
    env = request.scope["env"]
    client = D1Client(env.DB)
    _ensure_table(table)
    await client.execute(queries.delete_base(table), item_id)
    return {"id": item_id, "status": "deleted"}


def _ensure_table(table: str) -> None:
    if table not in TABLE_CONFIG:
        raise HTTPException(status_code=404, detail=f"Unknown table: {table}")
