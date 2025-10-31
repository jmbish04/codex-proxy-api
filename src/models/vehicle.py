"""Pydantic models describing vehicle telemetry tables."""
from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field


class TimestampedModel(BaseModel):
    id: str = Field(..., description="Unique identifier")
    created_at: Optional[str] = Field(None, description="Creation timestamp")
    updated_at: Optional[str] = Field(None, description="Last update timestamp")


class Vehicle(TimestampedModel):
    vin: Optional[str] = Field(None, description="Vehicle VIN")
    display_name: Optional[str] = Field(None, description="Human readable name")


class VehicleSettings(TimestampedModel):
    vehicle_id: Optional[str] = Field(None, description="Related vehicle id")
    data: Optional[dict] = Field(None, description="Arbitrary settings blob")


class Charge(TimestampedModel):
    vehicle_id: Optional[str] = Field(None)
    battery_level: Optional[float] = Field(None)
    charge_energy_added: Optional[float] = Field(None)


class Drive(TimestampedModel):
    vehicle_id: Optional[str] = Field(None)
    distance_miles: Optional[float] = Field(None)
    duration_seconds: Optional[int] = Field(None)


class Climate(TimestampedModel):
    vehicle_id: Optional[str] = Field(None)
    inside_temp_c: Optional[float] = Field(None)
    outside_temp_c: Optional[float] = Field(None)


class SoftwareUpdate(TimestampedModel):
    vehicle_id: Optional[str] = Field(None)
    version: Optional[str] = Field(None)
    status: Optional[str] = Field(None)
