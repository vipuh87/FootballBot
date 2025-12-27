# application/services/update_scheduler.py
import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime, timedelta, date, timezone

from data.selected_teams import  SELECTED_TEAM_IDS
from config import REMINDER_MINUTES_BEFORE

logger = logging.getLogger(__name__)

class UpdateScheduler:
    def __init__(self, api, cache, limiter, push, bot, repo):
        self.api = api
        self.cache = cache
        self.limiter = limiter
        self.push = push
        self.bot = bot
        self.scheduler = AsyncIOScheduler()
        self.repo = repo

    def start(self):
        # Ранкове оновлення (змінюй час на 9:00 коли тест закінчиться)
        self.scheduler.add_job(
            self.morning_update,
            "cron",
            hour=9,
            minute=00,
            timezone="Europe/Kyiv"
        )

        self.scheduler.start()

    async def schedule_reminders_for_day(self, day: date):
        """Планує нагадування для всіх матчів дня з SELECTED_TEAM_IDS"""
        matches = await self.repo.list_matches_for_day(day)

        for match in matches:
            if str(match.fixture_id) in self.push.sent:
                continue

            home_id = match.home_id
            away_id = match.away_id

            if home_id not in SELECTED_TEAM_IDS and away_id not in SELECTED_TEAM_IDS:
                continue

            if not match.date_utc:
                continue

            try:
                match_start_utc = datetime.fromisoformat(match.date_utc.replace("Z", "+00:00"))
                reminder_time_utc = match_start_utc - timedelta(minutes=REMINDER_MINUTES_BEFORE)

                if reminder_time_utc < datetime.now(timezone.utc):
                    continue  # якщо вже пройшло — пропускаємо

                # Унікальний ID job'а по fixture_id
                job_id = f"reminder_{match.fixture_id}"

                self.scheduler.add_job(
                    self.push.send_reminder_for_match,
                    "date",
                    run_date=reminder_time_utc,
                    timezone="UTC",
                    id=job_id,
                    replace_existing=True,  # якщо матч оновився — перезаписуємо
                    args=[match]  # передаємо готовий об'єкт match
                )

                print(f"Заплановано нагадування для матчу {match.fixture_id} на {reminder_time_utc}")
            except Exception as e:
                print(f"Помилка планування нагадування для {match.fixture_id}: {e}")

    async def morning_update(self):
        await self._update_days(-1, 0, 1)
        await self._update_yesterday_details()
        await self.push.send_morning_digest()

        logger.info("Ранкове оновлення та надсилання дайджесту завершено")

        today = date.today()
        await self.schedule_reminders_for_day(today)
        await self.schedule_reminders_for_day(today + timedelta(days=1))

    async def _update_days(self, *offsets):
        for offset in offsets:
            day = date.today() + timedelta(days=offset)
            print(f"🔄 UPDATING DAY {day} (offset {offset})")

            try:
                # Використовуємо існуючий метод repo, який робить запит і зберігає
                await self.repo.refresh_day(day,self.api)

                matches = await self.repo.list_matches_for_day(day)
                print(f"✅ SAVED {len(matches)} матчів для {day} після фільтрації")

            except Exception as e:
                print(f"❌ ERROR updating day {day}: {e}")

    async def _update_yesterday_details(self):
        from application.container import Container

        details_service = Container.get().match_details

        yesterday = datetime.now().date() - timedelta(days=1)
        matches = await self.repo.list_matches_for_day(yesterday)

        updated_count = 0
        for match in matches:
            try:
                updated_match = await details_service.ensure_details(match)
                if updated_match != match:
                    updated_count += 1
                print(f"✅ UPDATED DETAILS for match {match.fixture_id}")
            except Exception as e:
                print(f"❌ DETAILS UPDATE ERROR for match {match.fixture_id}: {e}")

        print(f"✅ Оновлено деталі для {updated_count} вчорашніх матчів")