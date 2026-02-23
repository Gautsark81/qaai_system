# path: qaai_system/config/broker_factory.py
from __future__ import annotations

import os
from typing import Protocol

from dhanhq import dhanhq  # or your wrapped client

from qaai_system.broker.dhan_safe_client import DhanSafeClient, DhanSafeConfig


class SettingsLike(Protocol):
    DHAN_CLIENT_ID: str
    DHAN_ACCESS_TOKEN: str

    DHAN_MAX_RETRIES: int
    DHAN_BASE_BACKOFF_SECONDS: float
    DHAN_MAX_BACKOFF_SECONDS: float
    DHAN_MAX_REQUESTS_PER_SEC: int
    DHAN_IDEMPOTENCY_TTL_SECONDS: int


def _get_env_or(settings: object, name: str, default: str) -> str:
    val = getattr(settings, name, None)
    if val:
        return str(val)
    return os.getenv(name, default)


def build_dhan_safe_client(settings: SettingsLike) -> DhanSafeClient:
    client_id = _get_env_or(settings, "DHAN_CLIENT_ID", "")
    access_token = _get_env_or(settings, "DHAN_ACCESS_TOKEN", "")

    if not client_id or not access_token:
        raise ValueError(
            "DHAN_CLIENT_ID and DHAN_ACCESS_TOKEN must be provided via "
            "settings or environment variables."
        )

    cfg = DhanSafeConfig(
        client_id=client_id,
        access_token=access_token,
        max_retries=int(getattr(settings, "DHAN_MAX_RETRIES", 3)),
        base_backoff_seconds=float(
            getattr(settings, "DHAN_BASE_BACKOFF_SECONDS", 0.5)
        ),
        max_backoff_seconds=float(
            getattr(settings, "DHAN_MAX_BACKOFF_SECONDS", 3.0)
        ),
        max_requests_per_sec=int(
            getattr(settings, "DHAN_MAX_REQUESTS_PER_SEC", 10)
        ),
        idempotency_ttl_seconds=int(
            getattr(settings, "DHAN_IDEMPOTENCY_TTL_SECONDS", 600)
        ),
    )

    raw = dhanhq(client_id=cfg.client_id, access_token=cfg.access_token)
    return DhanSafeClient(config=cfg, raw_client=raw)
