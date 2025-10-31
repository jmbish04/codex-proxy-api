"""Logging and auxiliary table models."""
from __future__ import annotations

from typing import Any, Optional

from pydantic import BaseModel, Field


class LogRow(BaseModel):
    id: str = Field(...)
    route: Optional[str] = None
    actor: Optional[str] = None
    request_id: Optional[str] = None
    level: str = "INFO"
    message: str
    payload: Optional[Any] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class TessieRaw(BaseModel):
    id: str
    vehicle_id: Optional[str] = None
    endpoint: Optional[str] = None
    payload: Optional[str] = None


class SyncRun(BaseModel):
    id: str
    status: Optional[str] = None
    started_at: Optional[str] = None
    finished_at: Optional[str] = None


class EnergyReport(BaseModel):
    id: str
    vehicle_id: Optional[str] = None
    total_energy_added: Optional[float] = None
    average_energy_added: Optional[float] = None
    samples: Optional[int] = None
