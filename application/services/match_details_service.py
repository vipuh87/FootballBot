from datetime import datetime, timezone


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

        if match.date_utc:
            try:
                match_start_utc = datetime.fromisoformat(match.date_utc.replace("Z", "+00:00"))
                now_utc = datetime.now(timezone.utc)
                minutes_to_start = (match_start_utc - now_utc).total_seconds() / 60
            except Exception as e:
                print(f"⚠️ Помилка парсингу дати матчу {match.fixture_id}: {e}")
                minutes_to_start = -999  # якщо не вдалося — дозволити запит (безпечніше)
        else:
            minutes_to_start = -999  # якщо дати немає — дозволити

            # Lineups — тільки якщо матч уже почався або починається протягом 30 хвилин
        if not match.lineups and minutes_to_start <= 30:
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