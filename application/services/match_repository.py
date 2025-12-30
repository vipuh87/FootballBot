# services/match_repository.py
from __future__ import annotations
from datetime import date
from typing import Optional, List, Dict, Any

from application.services.cache_service import CacheService
from application.services.match_factory import matches_from_api_day
from domain.models.match import Match


class MatchRepository:

    def __init__(self, cache: CacheService):
        self.cache = cache

    async def list_matches_for_day(self, day: date) -> List[Match]:
        raw = await self.cache.read_day(day)
        if not raw or not isinstance(raw, dict):
            return []
        return matches_from_api_day(raw)

    async def find_match(self, fixture_id: int, day: Optional[date] = None) -> Optional[Match]:
        if day:
            matches = await self.list_matches_for_day(day)
            for m in matches:
                if m.fixture_id == fixture_id:
                    return m
            return None

        from datetime import date as _date, timedelta
        today = _date.today()
        for off in (0, 1, -1):
            d = today + timedelta(days=off)
            matches = await self.list_matches_for_day(d)
            for m in matches:
                if m.fixture_id == fixture_id:
                    return m
        return None

    async def save_match(self, match: Match, day: Optional[date] = None) -> None:
        from datetime import datetime, timezone, date as _date

        if day is None:
            if match.date_utc:
                try:
                    dt = datetime.fromisoformat(match.date_utc.replace("Z", "+00:00"))
                    day = dt.date()
                except Exception:
                    day = _date.today()
            else:
                day = _date.today()

        raw = await self.cache.read_day(day) or {}
        resp = raw.get("response", []) if isinstance(raw, dict) else []

        updated = False
        new_wrapper = match.to_api_fixture_wrapper()

        for i, item in enumerate(resp):
            try:
                fid = (item.get("fixture") or {}).get("id")
                if fid == match.fixture_id:
                    resp[i] = new_wrapper
                    updated = True
                    break
            except Exception:
                continue

        if not updated:
            resp.append(new_wrapper)

        raw["response"] = resp
        await self.cache.write_day(day, raw)

    async def update_lineups(self, fixture_id: int, lineups: List[Dict[str, Any]], day: Optional[date] = None) -> None:
        m = await self.find_match(fixture_id, day)
        if not m:
            return
        m.lineups = lineups
        await self.save_match(m, day)

    async def update_events(self, fixture_id: int, events: List[Dict[str, Any]], day: Optional[date] = None) -> None:
        m = await self.find_match(fixture_id, day)
        if not m:
            return
        m.events = events
        await self.save_match(m, day)

    async def update_statistics(self, fixture_id: int, statistics: List[Dict[str, Any]], day: Optional[date] = None) -> None:
        m = await self.find_match(fixture_id, day)
        if not m:
            return
        m.statistics = statistics
        await self.save_match(m, day)

    # ✅ ОТРИМАТИ МАТЧІ З АВТОЗАПИТОМ В API
    async def get_matches_by_date(self, day: date, api) -> list[Match]:
        raw = await self.cache.read_day(day)

        if not raw:
            raw = await api.fixtures_by_date(day)
            await self.cache.write_day(day, raw)

        return matches_from_api_day(raw)

    # ✅ ЗНАЙТИ МАТЧ ЯК unwrap для handler
    async def find_match_by_id(self, fixture_id: int) -> Match | None:
        return await self.find_match(fixture_id)

    # ✅ ЧАС ОСТАННЬОГО ОНОВЛЕННЯ
    async def get_last_update(self, day: date):
        return await self.cache.get_last_update_time(day)

    # ✅ ПРИМУСОВЕ ОНОВЛЕННЯ ДНЯ
    async def refresh_day(self, day: date, api):
        print(f"🔄 START REFRESH DAY {day}")

        raw = await api.fixtures_by_date(day)

        if not raw or not raw.get("response"):
            print(f"❌ NO RAW DATA for {day}")
            return

        print(f"✅ RECEIVED {len(raw['response'])} fixtures from API for {day}")

        # Зберігаємо повний raw в кеш (щоб при list_matches_for_day фільтрувати з повних даних)
        await self.cache.write_day(day, raw)

        print(f"✅ SAVED full raw data for {day} to cache")
