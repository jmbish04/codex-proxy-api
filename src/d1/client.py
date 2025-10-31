"""Thin asynchronous client wrappers for Cloudflare D1."""
from __future__ import annotations

from typing import Any, Dict, List, Optional


class D1Client:
    """Helper utility to simplify parameter binding with D1."""

    def __init__(self, binding: Any):
        self.binding = binding

    def prepare(self, sql: str, *params: Any):
        stmt = self.binding.prepare(sql)
        if params:
            stmt = stmt.bind(*params)
        return stmt

    async def execute(self, sql: str, *params: Any) -> Dict[str, Any]:
        stmt = self.prepare(sql, *params)
        result = await stmt.run()
        return _normalize_result(result)

    async def fetch_all(self, sql: str, *params: Any) -> List[Dict[str, Any]]:
        stmt = self.prepare(sql, *params)
        result = await stmt.all()
        return result.get("results", []) if isinstance(result, dict) else []

    async def fetch_one(self, sql: str, *params: Any) -> Optional[Dict[str, Any]]:
        stmt = self.prepare(sql, *params)
        result = await stmt.first()
        if isinstance(result, dict):
            return result
        if isinstance(result, list) and result:
            first = result[0]
            return first if isinstance(first, dict) else None
        return None


def _normalize_result(result: Any) -> Dict[str, Any]:
    if isinstance(result, dict):
        return result
    return {"ok": True, "raw": result}


async def log_row(binding: Any, table: str, payload: Dict[str, Any]) -> None:
    columns = list(payload.keys())
    placeholders = ", ".join(columns)
    values = tuple(payload[column] for column in columns)
    question_marks = ", ".join(["?"] * len(values))
    sql = f"INSERT INTO {table} ({placeholders}) VALUES ({question_marks})"
    stmt = binding.prepare(sql).bind(*values)
    await stmt.run()
