# infrastructure/storage/redis_adapter.py
import json
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
from datetime import date

import redis.asyncio as redis

from config import CACHE_RETENTION_DAYS
from infrastructure.storage.base_adapter import CacheAdapter


class RedisCacheAdapter(CacheAdapter):
    TTL_DAYS = CACHE_RETENTION_DAYS

    def __init__(self, redis_client: redis.Redis):
        self.client = redis_client

    def _key_data(self, day: date) -> str:
        return f"match_day:{day.isoformat()}:data"

    def _key_timestamp(self, day: date) -> str:
        return f"match_day:{day.isoformat()}:ts"

    async def write_day(self, day: date, data: Dict[Any, Any]) -> None:
        key_data = self._key_data(day)
        key_ts = self._key_timestamp(day)
        json_data = json.dumps(data, ensure_ascii=False)
        ttl_seconds = int(timedelta(days=self.TTL_DAYS).total_seconds())

        now_utc_iso = datetime.now(timezone.utc).isoformat()

        await self.client.set(key_data, json_data, ex=ttl_seconds)
        await self.client.set(key_ts, now_utc_iso, ex=ttl_seconds)

    async def read_day(self, day: date) -> Optional[Dict[Any, Any]]:
        key = self._key_data(day)
        data = await self.client.get(key)
        if data is None:
            return None
        return json.loads(data)

    async def get_last_update_time(self, day: date) -> Optional[datetime]:
        key_ts = self._key_timestamp(day)
        ts_str = await self.client.get(key_ts)
        if ts_str is None:
            return None
        # Підтримуємо як з Z, так і без
        ts_str = ts_str.decode('utf-8') if isinstance(ts_str, bytes) else ts_str
        ts_str = ts_str.replace("Z", "+00:00") if "Z" in ts_str else ts_str
        return datetime.fromisoformat(ts_str)

    async def cleanup_old(self) -> None:
        # Redis сам видаляє за TTL
        pass