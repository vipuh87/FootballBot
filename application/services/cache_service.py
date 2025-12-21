# application/services/cache_service.py
from datetime import date
from typing import Optional, Dict, Any

from infrastructure.storage.base_adapter import CacheAdapter

class CacheService:
    def __init__(self, adapter: CacheAdapter):
        self.adapter = adapter

    async def read_day(self, day: date) -> Optional[Dict[Any, Any]]:
        return await self.adapter.read_day(day)

    async def write_day(self, day: date, data: Dict[Any, Any]) -> None:
        await self.adapter.write_day(day, data)

    async def get_last_update_time(self, day: date):
        return await self.adapter.get_last_update_time(day)

    async def cleanup_old(self):
        await self.adapter.cleanup_old()

    # Зберігаємо твої методи update_match_section тощо — вони працюють з read/write_day
    # (якщо потрібно — можемо перенести їх в адаптер пізніше)
    async def update_match_section(self, day: date, fixture_id: int, field: str, value: Any) -> None:
        raw = await self.read_day(day)
        if not raw or not isinstance(raw, dict):
            return

        response = raw.get("response", [])
        changed = False

        for match in response:
            fid = (match.get("fixture") or {}).get("id")
            if fid == fixture_id:
                match[field] = value
                changed = True
                break

        if changed:
            raw["response"] = response
            self.write_day(day, raw)

    # save_lineups, save_events, save_statistics — залишаємо як є
    def save_lineups(self, day: date, fixture_id: int, lineups: list) -> None:
        self.update_match_section(day, fixture_id, "lineups", lineups)

    def save_events(self, day: date, fixture_id: int, events: list) -> None:
        self.update_match_section(day, fixture_id, "events", events)

    def save_statistics(self, day: date, fixture_id: int, statistics: list) -> None:
        self.update_match_section(day, fixture_id, "statistics", statistics)