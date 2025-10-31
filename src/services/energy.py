"""Energy report generation routines."""
from __future__ import annotations

import statistics
import uuid
from typing import Any, Dict

from src.d1.client import D1Client


async def generate_energy_report(env: Any, vehicle_id: str) -> Dict[str, Any]:
    client = D1Client(env.DB)
    charges = await client.fetch_all(
        "SELECT charge_energy_added FROM charges WHERE vehicle_id = ? ORDER BY created_at DESC LIMIT 100",
        vehicle_id,
    )
    values = [row.get("charge_energy_added") for row in charges if row.get("charge_energy_added") is not None]
    total = float(sum(values)) if values else 0.0
    avg = float(statistics.mean(values)) if values else 0.0
    samples = len(values)
    report_id = str(uuid.uuid4())
    await client.execute(
        """
        INSERT INTO energy_reports (id, vehicle_id, total_energy_added, average_energy_added, samples, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
        """,
        report_id,
        vehicle_id,
        total,
        avg,
        samples,
    )
    return {
        "id": report_id,
        "vehicle_id": vehicle_id,
        "total_energy_added": total,
        "average_energy_added": avg,
        "samples": samples,
    }
