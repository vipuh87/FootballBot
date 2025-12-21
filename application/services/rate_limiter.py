from datetime import datetime, timedelta

class RateLimiterService:
    def __init__(self, api_client, cache_ttl_seconds: int = 60):
        self.api = api_client
        self._cache = None
        self._expires = datetime.min
        self.ttl = timedelta(seconds=cache_ttl_seconds)

    async def get_status(self) -> dict:
        try:
            st = await self.api.status()
        except Exception:
            st = {}
        return st

    async def remaining_requests(self) -> int:
        st = await self.get_status()
        # try several possible shapes
        try:
            # new shape
            cur = int(st.get('response', {}).get('requests', {}).get('current', 90))
            lim = int(st.get('response', {}).get('requests', {}).get('limit_day', 100))
            rem = lim-cur
        except Exception:
            rem = 0
        return rem

    async def allow_manual_update(self, min_allowed: int) -> bool:
        rem = await self.remaining_requests()
        return rem >= min_allowed
