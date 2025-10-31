"""Reusable SQL templates for D1 interactions."""
from __future__ import annotations

from typing import Dict


TABLES = {
    "vehicles": "vehicles",
    "vehicle_settings": "vehicle_settings",
    "charges": "charges",
    "drives": "drives",
    "climates": "climates",
    "software_updates": "software_updates",
    "tessie_raw": "tessie_raw",
    "sync_runs": "sync_runs",
    "energy_reports": "energy_reports",
    "logs": "logs",
    "agent_messages": "agent_messages",
    "agent_actions": "agent_actions",
}


def select_base(table: str) -> str:
    return f"SELECT * FROM {TABLES[table]}"


def select_by_id(table: str) -> str:
    return f"SELECT * FROM {TABLES[table]} WHERE id = ?"


def insert_base(table: str, columns: Dict[str, str]) -> str:
    keys = ", ".join(columns.keys())
    placeholders = ", ".join(["?"] * len(columns))
    return f"INSERT INTO {TABLES[table]} ({keys}) VALUES ({placeholders})"


def update_base(table: str, columns: Dict[str, str]) -> str:
    sets = ", ".join([f"{key} = ?" for key in columns.keys() if key != "id"])
    return f"UPDATE {TABLES[table]} SET {sets} WHERE id = ?"


def delete_base(table: str) -> str:
    return f"DELETE FROM {TABLES[table]} WHERE id = ?"
