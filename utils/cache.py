"""Lightweight Redis cache helper with graceful degradation when Redis is unavailable."""
from __future__ import annotations

import json
from functools import lru_cache
from typing import Any, Optional

import redis

from utils import get_logger, settings

logger = get_logger("cache")


@lru_cache(maxsize=1)
def get_client() -> Optional[redis.Redis]:
    """Return a Redis client or None if Redis is unreachable."""
    try:
        client = redis.Redis.from_url(settings.redis_url, decode_responses=True)
        client.ping()
        return client
    except Exception as exc:  # pragma: no cover - defensive
        logger.warning("Redis unavailable: %s", exc)
        return None


def get(key: str) -> Optional[Any]:
    client = get_client()
    if not client:
        return None
    try:
        value = client.get(key)
        return json.loads(value) if value else None
    except Exception as exc:  # pragma: no cover
        logger.warning("Redis get failed for %s: %s", key, exc)
        return None


def set(key: str, value: Any, ttl_seconds: int = 300) -> None:
    client = get_client()
    if not client:
        return
    try:
        client.set(key, json.dumps(value), ex=ttl_seconds)
    except Exception as exc:  # pragma: no cover
        logger.warning("Redis set failed for %s: %s", key, exc)


def delete(key: str) -> None:
    client = get_client()
    if not client:
        return
    try:
        client.delete(key)
    except Exception as exc:  # pragma: no cover
        logger.warning("Redis delete failed for %s: %s", key, exc)


def delete_prefix(prefix: str) -> None:
    client = get_client()
    if not client:
        return
    try:
        cursor = 0
        pattern = f"{prefix}*"
        while True:
            cursor, keys = client.scan(cursor=cursor, match=pattern, count=200)
            if keys:
                client.delete(*keys)
            if cursor == 0:
                break
    except Exception as exc:  # pragma: no cover
        logger.warning("Redis delete_prefix failed for %s: %s", prefix, exc)


def is_healthy() -> bool:
    client = get_client()
    if not client:
        return False
    try:
        client.ping()
        return True
    except Exception:
        return False
