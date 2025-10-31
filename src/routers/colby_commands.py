"""Curated automation routines."""
from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request

from src.services.energy import generate_energy_report

router = APIRouter(prefix="/colbycommands", tags=["colbycommands"])


@router.post("/energy-report")
async def energy_report(request: Request):
    env = request.scope["env"]
    payload = await request.json()
    vehicle_id = payload.get("vehicle_id")
    if not vehicle_id:
        raise HTTPException(status_code=400, detail="vehicle_id is required")
    report = await generate_energy_report(env, vehicle_id)
    return {"report": report}
