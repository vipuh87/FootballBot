import aiohttp
from typing import Dict, Any
from datetime import date
from config import API_SPORTS_BASE, HEADERS
from application.services.team_service import is_selected_team

class ApiClient:
    def __init__(self):
        self.base = API_SPORTS_BASE

    async def _get(self, path: str, params: Dict = None) -> Dict[str, Any]:
        url = self.base + path
        async with aiohttp.ClientSession(headers=HEADERS) as sess:
            async with sess.get(url, params=params, timeout=20) as resp:
                resp.raise_for_status()
                return await resp.json()

    async def fixtures_by_date(self, target_date: date) -> Dict:
        return await self._get('/fixtures', params={'date': target_date.isoformat()})

    async def events_by_fixture(self, fixture_id: int) -> Dict:
        return await self._get('/fixtures/events', params={'fixture': fixture_id})

    async def statistics_by_fixture(self, fixture_id: int) -> Dict:
        return await self._get('/fixtures/statistics', params={'fixture': fixture_id})

    async def lineup_by_fixture(self, fixture_id: int) -> Dict:
        return await self._get('/fixtures/lineups', params={'fixture': fixture_id})

    async def status(self) -> Dict:
        return await self._get('/status')
