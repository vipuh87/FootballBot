# application/services/update_scheduler.py
import asyncio
import json
import logging
from pathlib import Path
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime, timedelta, date, timezone

from data.selected_teams import get_selected_team_ids
from config import REMINDER_MINUTES_BEFORE, REMINDER_TOLERANCE_MINUTES, TZ_UKRAINE

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
        # Ранкове оновлення
        self.scheduler.add_job(
            self.morning_update,
            "cron",
            hour=9,
            minute=0,
            timezone="Europe/Kyiv"
        )
        self.scheduler.add_job(
            self.send_prediction_reminders,
            "interval",
            minutes=30,
            timezone="UTC",
            id="prediction_reminders",
            replace_existing=True,
            misfire_grace_time=300,
        )

        self.scheduler.start()
        print("📅 Scheduler запущено")

        # ← ДОДАНО: перепланування нагадувань при старті бота
        asyncio.create_task(self.replan_all_reminders())
        asyncio.create_task(self.send_prediction_reminders())
        self.schedule_world_cup_result_updates()

    async def send_prediction_reminders(self):
        from application.services.predictions import PredictionService
        from presentation.keyboards.predictions import prediction_reminder_kb

        svc = PredictionService()
        reminders = svc.due_reminders()
        sent_keys = []

        for reminder in reminders:
            sent_any = False
            for target in self.push.push_targets:
                try:
                    kwargs = {
                        "parse_mode": "HTML",
                        "reply_markup": prediction_reminder_kb(reminder.get("fixture_id")),
                    }
                    if target.get("thread_id"):
                        kwargs["message_thread_id"] = int(target["thread_id"])

                    await self.bot.send_message(
                        chat_id=target["chat_id"],
                        text=reminder["text"],
                        **kwargs,
                    )
                    sent_any = True
                    await asyncio.sleep(0.1)
                except Exception as e:
                    print(f"Prediction reminder send error for {target['chat_id']}: {e}")

            if sent_any:
                sent_keys.append(reminder["key"])

        svc.mark_reminders_sent(sent_keys)

    async def run_cron_tick(self):
        await self.send_due_match_reminders()
        await self.send_prediction_reminders()
        await self.run_morning_update_if_due()

    async def run_morning_update_if_due(self):
        now_ua = datetime.now(TZ_UKRAINE)
        if now_ua.hour != 9:
            return False

        key = "morning_update"
        today_key = now_ua.date().isoformat()
        if await self._get_job_state(key) == today_key:
            return False

        await self.morning_update()
        await self._set_job_state(key, today_key)
        return True

    async def send_due_match_reminders(self):
        today = datetime.now(timezone.utc).date()
        sent = 0
        for day in (today, today + timedelta(days=1)):
            sent += await self._send_due_match_reminders_for_day(day)
        return sent

    async def _send_due_match_reminders_for_day(self, day: date):
        matches = await self.repo.list_matches_for_day(day)
        selected_team_ids = set(get_selected_team_ids(day))
        now = datetime.now(timezone.utc)
        lower = now - timedelta(minutes=REMINDER_TOLERANCE_MINUTES)
        upper = now + timedelta(minutes=REMINDER_TOLERANCE_MINUTES)
        sent = 0

        for match in matches:
            if await self.push.was_reminder_sent(match.fixture_id):
                continue
            if match.home_id not in selected_team_ids and match.away_id not in selected_team_ids:
                continue
            if not match.date_utc:
                continue

            try:
                match_start_utc = datetime.fromisoformat(match.date_utc.replace("Z", "+00:00"))
            except Exception:
                continue

            if match_start_utc.hour >= 20 or match_start_utc.hour < 6:
                continue

            reminder_time_utc = match_start_utc - timedelta(minutes=REMINDER_MINUTES_BEFORE)
            if lower <= reminder_time_utc <= upper:
                await self.push.send_reminder_for_match(match)
                sent += 1

        return sent

    async def _get_job_state(self, key: str):
        redis = getattr(self.cache.adapter, "client", None)
        if redis is not None:
            return await redis.get(f"job_state:{key}")

        state = self._read_local_job_state()
        return state.get(key)

    async def _set_job_state(self, key: str, value: str):
        redis = getattr(self.cache.adapter, "client", None)
        if redis is not None:
            await redis.set(f"job_state:{key}", value, ex=int(timedelta(days=14).total_seconds()))
            return

        state = self._read_local_job_state()
        state[key] = value
        path = Path("data/job_state.json")
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")

    def _read_local_job_state(self):
        path = Path("data/job_state.json")
        if not path.exists():
            return {}
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            return {}

    def schedule_world_cup_result_updates(self):
        from application.services.predictions import PredictionService

        svc = PredictionService()
        now = datetime.now(timezone.utc)
        planned = 0
        for match in svc.matches():
            try:
                kickoff = svc.kickoff(match)
            except Exception:
                continue

            run_at = kickoff + timedelta(minutes=150)
            if run_at <= now:
                continue

            self.scheduler.add_job(
                self.refresh_world_cup_match_after_finish,
                "date",
                run_date=run_at,
                timezone="UTC",
                id=f"wc_result_{match['fixture_id']}",
                replace_existing=True,
                args=[match["fixture_id"]],
                misfire_grace_time=3600,
            )
            planned += 1

        logger.info("Заплановано %s оновлень результатів ЧС-2026", planned)

    async def refresh_world_cup_match_after_finish(self, fixture_id: int):
        from application.services.predictions import PredictionService

        svc = PredictionService()
        match = svc.find_match(fixture_id)
        if not match:
            logger.warning("Не знайдено матч ЧС-2026 для оновлення: %s", fixture_id)
            return

        day = svc.kickoff(match).date()
        await self.repo.refresh_day(day, self.api)
        raw = await self.cache.read_day(day)
        updated = svc.sync_results_from_api_day(raw or {})
        logger.info("Оновлення ЧС-2026 після матчу %s: оновлено %s записів", fixture_id, updated)

    async def replan_all_reminders(self):
        """Перепланує нагадування для сьогодні і завтра при старті бота"""
        print("🔄 Перепланування нагадувань при старті бота...")

        today = date.today()
        await self.schedule_reminders_for_day(today)
        await self.schedule_reminders_for_day(today + timedelta(days=1))

        print("✅ Перепланування нагадувань завершено")

    async def schedule_reminders_for_day(self, day: date):
        """Планує нагадування для всіх матчів дня з SELECTED_TEAM_IDS"""
        matches = await self.repo.list_matches_for_day(day)
        selected_team_ids = set(get_selected_team_ids(day))

        print(f"Обробка {len(matches)} матчів для нагадувань на {day}")

        for match in matches:
            if str(match.fixture_id) in self.push.sent:
                print(f"Нагадування для {match.fixture_id} вже надіслано — пропускаємо")
                continue

            home_id = match.home_id
            away_id = match.away_id

            if home_id not in selected_team_ids and away_id not in selected_team_ids:
                continue

            if not match.date_utc:
                print(f"date_utc порожнє для матчу {match.fixture_id} — пропускаємо")
                continue

            try:
                match_start_utc = datetime.fromisoformat(match.date_utc.replace("Z", "+00:00"))

                # Пропускаємо нічні матчі для української аудиторії
                if match_start_utc.hour >= 20 or match_start_utc.hour < 6:
                    print(
                        f"Матч {match.fixture_id} стартує о "
                        f"{match_start_utc.strftime('%H:%M')} UTC "
                        f"(нічний час для України) — нагадування не плануємо"
                    )
                    continue

                reminder_time_utc = match_start_utc - timedelta(minutes=REMINDER_MINUTES_BEFORE)

                if reminder_time_utc < datetime.now(timezone.utc):
                    print(f"Час нагадування для {match.fixture_id} вже минув — пропускаємо")
                    continue

                job_id = f"reminder_{match.fixture_id}"

                self.scheduler.add_job(
                    self.push.send_reminder_for_match,
                    "date",
                    run_date=reminder_time_utc,
                    timezone="UTC",
                    id=job_id,
                    replace_existing=True,
                    args=[match],
                    misfire_grace_time = 300
                )

                print(f"✅ Заплановано нагадування для матчу {match.fixture_id} ({match.home} — {match.away}) на {reminder_time_utc}")

            except Exception as e:
                print(f"❌ Помилка планування для {match.fixture_id}: {e}")

    async def morning_update(self):
        await self._update_days(-1, 0, 1)
        await self._update_yesterday_details()
        await self.push.send_morning_digest()

        # Переплануємо нагадування після оновлення даних
        today = date.today()
        await self.schedule_reminders_for_day(today)
        await self.schedule_reminders_for_day(today + timedelta(days=1))

        logger.info("Ранкове оновлення та планування нагадувань завершено")

    # _update_days і _update_yesterday_details — залишаються без змін
    async def _update_days(self, *offsets):
        for offset in offsets:
            day = date.today() + timedelta(days=offset)
            print(f"🔄 UPDATING DAY {day} (offset {offset})")

            try:
                await self.repo.refresh_day(day, self.api)
                raw = await self.cache.read_day(day)
                from application.services.predictions import PredictionService
                PredictionService().sync_results_from_api_day(raw or {})

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
