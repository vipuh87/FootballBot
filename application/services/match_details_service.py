# application/services/match_details_service.py
class MatchDetailsService:
    def __init__(self, repo, api):
        self.repo = repo
        self.api = api

    async def ensure_details(self, match):
        """
        Оновлює деталі матчу з API, якщо їх немає в кеші.
        - lineups: завжди (для нагадувань)
        - events & statistics: тільки якщо матч завершений (FT, AET, PEN)
        """
        if not match:
            return match

        updated = False

        # Lineups — завжди
        if not match.lineups:
            lineups_raw = await self.api.lineup_by_fixture(match.fixture_id)
            if lineups_raw.get("response"):
                await self.repo.update_lineups(match.fixture_id, lineups_raw["response"])
                updated = True

        # Events і stats — тільки для завершених
        if match.status in ("FT", "AET", "PEN"):
            if not match.events:
                events_raw = await self.api.events_by_fixture(match.fixture_id)
                if events_raw.get("response"):
                    await self.repo.update_events(match.fixture_id, events_raw["response"])
                    updated = True

            if not match.statistics:
                stats_raw = await self.api.statistics_by_fixture(match.fixture_id)
                if stats_raw.get("response"):
                    await self.repo.update_statistics(match.fixture_id, stats_raw["response"])
                    updated = True

        if updated:
            return await self.repo.find_match_by_id(match.fixture_id)

        return match