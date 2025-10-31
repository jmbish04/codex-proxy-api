"""Configuration utilities for the Worker application."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List


@dataclass
class Settings:
    """Runtime configuration derived from the Worker environment."""

    cors_allowed_origins: List[str]


def _get_env_attr(env: object, key: str, default: str | None = None) -> str | None:
    if hasattr(env, key):
        value = getattr(env, key)
        if isinstance(value, str):
            return value
    if isinstance(env, dict):
        raw = env.get(key, default)
        if isinstance(raw, str) or raw is None:
            return raw
    return default


def parse_csv(value: str | None) -> List[str]:
    if not value:
        return []
    items: Iterable[str] = (item.strip() for item in value.split(","))
    return [item for item in items if item]


def get_settings(env: object) -> Settings:
    cors = _get_env_attr(env, "CORS_ALLOWED_ORIGINS", "")
    return Settings(cors_allowed_origins=parse_csv(cors))
