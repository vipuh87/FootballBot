# application/services/update_scheduler.py
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime, timedelta, date
from application.container import Container

class UpdateScheduler:
    def __init__(self, api, cache, limiter, push, bot):
        self.api = api
        self.cache = cache
        self.limiter = limiter
        self.push = push
        self.bot = bot
        self.scheduler = AsyncIOScheduler()

    def start(self):
        # Ранкове оновлення (змінюй час на 9:00 коли тест закінчиться)
        self.scheduler.add_job(
            self.morning_update,
            "cron",
            hour=13,
            minute=32,
            timezone="Europe/Kyiv"
        )

        # Нагадування
        self.scheduler.add_job(
            self.push.scan_and_send_reminders,
            "interval",
            minutes=1
        )

        self.scheduler.start()
        print("📅 Scheduler запущено")

    async def morning_update(self):
        await self._update_days(-1, 0, 1)
        await self._update_yesterday_details()

    async def _update_days(self, *offsets):
        repo = Container.get().repo
        api = Container.get().api  # ← Об’єкт ApiClient

        for offset in offsets:
            day = date.today() + timedelta(days=offset)
            print(f"🔄 UPDATING DAY {day} (offset {offset})")

            try:
                # Використовуємо існуючий метод repo, який робить запит і зберігає
                await repo.refresh_day(day, api)

                matches = await repo.list_matches_for_day(day)
                print(f"✅ SAVED {len(matches)} матчів для {day} після фільтрації")

            except Exception as e:
                print(f"❌ ERROR updating day {day}: {e}")

    async def _update_yesterday_details(self):
        details_service = Container.get().match_details
        repo = Container.get().repo

        yesterday = datetime.now().date() - timedelta(days=1)
        matches = await repo.list_matches_for_day(yesterday)

        updated_count = 0
        for match in matches:
            try:
                updated_match = await details_service.ensure_details(match)
                if updated_match != match:  # Якщо щось змінилось
                    updated_count += 1
                print(f"✅ UPDATED DETAILS for match {match.fixture_id}")
            except Exception as e:
                print(f"❌ DETAILS UPDATE ERROR for match {match.fixture_id}: {e}")

        print(f"✅ Оновлено деталі для {updated_count} вчорашніх матчів")