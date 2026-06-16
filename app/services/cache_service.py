"""Redis cache wrapper with graceful local-development fallback."""

import json
import logging
from typing import Any

from redis.asyncio import Redis

from app.core.config import get_settings

logger = logging.getLogger(__name__)


class CacheService:
    def __init__(self) -> None:
        self._redis = Redis.from_url(get_settings().redis_url, decode_responses=True)

    async def get_json(self, key: str) -> Any | None:
        try:
            value = await self._redis.get(key)
        except Exception as exc:
            logger.warning("Redis get failed: %s", exc)
            return None
        return json.loads(value) if value else None

    async def set_json(self, key: str, value: Any, ttl_seconds: int = 300) -> None:
        try:
            await self._redis.setex(key, ttl_seconds, json.dumps(value))
        except Exception as exc:
            logger.warning("Redis set failed: %s", exc)

    async def close(self) -> None:
        await self._redis.aclose()
