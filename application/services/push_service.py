# application/services/push_service.py
import json
from pathlib import Path
from datetime import datetime, timedelta, timezone
from typing import Dict, List

from aiogram import Bot
import asyncio
import logging

from presentation.views.push import render_reminder_text
from config import (
    REMINDERS_FILE,
    PUSH_TARGETS,
    TZ_UKRAINE,
    REMINDER_MINUTES_BEFORE,
    REMINDER_TOLERANCE_MINUTES,
)
from data.selected_teams import SELECTED_TEAM_IDS
from application.services.players_service import get_ukrainian_players_for_match

logger = logging.getLogger(__name__)
REM_PATH = Path(REMINDERS_FILE)

class PushService:
    push_targets: List[Dict[str, int]]

    def __init__(self, bot: Bot):
        self.bot = bot
        self.sent = self._load_sent()
        self.push_targets = PUSH_TARGETS

    def _load_sent(self) -> Dict:
        if REM_PATH.exists():
            try:
                return json.loads(REM_PATH.read_text(encoding="utf-8"))
            except Exception as e:
                print(f"⚠️ Не вдалося прочитати {REMINDERS_FILE}: {e}")
                return {}
        return {}

    def _save_sent(self):
        try:
            REM_PATH.parent.mkdir(parents=True, exist_ok=True)
            REM_PATH.write_text(
                json.dumps(self.sent, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
        except Exception as e:
            print(f"⚠️ Не вдалося зберегти {REMINDERS_FILE}: {e}")

    async def scan_and_send_reminders(self):
        from application.container import Container

        now_utc = datetime.now(timezone.utc)
        repo = Container.get().repo

        lower_bound = REMINDER_MINUTES_BEFORE - REMINDER_TOLERANCE_MINUTES
        upper_bound = REMINDER_MINUTES_BEFORE + REMINDER_TOLERANCE_MINUTES

        for offset in (0, 1):
            target_date = (datetime.now(TZ_UKRAINE).date() + timedelta(days=offset))

            raw_data = await repo.cache.read_day(target_date)
            if not raw_data:
                continue

            fixtures = raw_data.get("response", [])

            for fixture in fixtures:
                try:
                    fid = fixture.get("fixture", {}).get("id")
                    start_utc_str = fixture.get("fixture", {}).get("date")

                    if not fid or not start_utc_str:
                        continue

                    if str(fid) in self.sent:
                        continue

                    match_start_utc = datetime.fromisoformat(start_utc_str.replace("Z", "+00:00"))

                    diff_minutes = (match_start_utc - now_utc).total_seconds() / 60

                    if not (lower_bound <= diff_minutes <= upper_bound):
                        continue

                    match = await repo.find_match_by_id(fid)
                    if not match:
                        continue

                    home_id = fixture.get("teams", {}).get("home", {}).get("id")
                    away_id = fixture.get("teams", {}).get("away", {}).get("id")

                    # НАГАДУВАННЯ НА КОЖЕН МАТЧ З SELECTED_TEAM_IDS
                    if home_id not in SELECTED_TEAM_IDS and away_id not in SELECTED_TEAM_IDS:
                        continue

                    # ua_info — тільки для тексту, не фільтр
                    ua_info = await get_ukrainian_players_for_match(match)

                    text = render_reminder_text(match, ua_info)  # ua_info може бути [] — рендер обробить

                    await self._send_plain(text)

                    self.sent[str(fid)] = {
                        "sent_at": datetime.now(TZ_UKRAINE).isoformat(),
                        "match_time_utc": start_utc_str,
                    }
                    self._save_sent()

                    print(f"✅ Нагадування надіслано для матчу {fid} ({match.home} — {match.away})")

                except Exception as e:
                    print(f"🔥 Помилка при обробці матчу {fid}: {e}")

    async def _send_plain(self, text: str):
        for target in PUSH_TARGETS:
            try:
                kwargs = {"parse_mode": "HTML"}
                if target.get("thread_id"):
                    kwargs["message_thread_id"] = int(target["thread_id"])

                await self.bot.send_message(
                    chat_id=target["chat_id"],
                    text=text,
                    **kwargs
                )
            except Exception as e:
                print(f"❌ Помилка надсилання в {target['chat_id']}: {e}")

    async def send_morning_digest(self):
        """Надсилає ранковий дайджест з новинами за вчора + головна клавіатура"""
        from presentation.views.digest_view import render_main_digest  # імпорт тут, щоб уникнути циклічного імпорту

        text, kb = await render_main_digest()

        for target in self.push_targets:
            chat_id = target["chat_id"]
            try:
                await self.bot.send_message(
                    chat_id=chat_id,
                    text=text,
                    reply_markup=kb,
                    parse_mode="HTML",
                    disable_web_page_preview=True
                )
                await asyncio.sleep(0.1)
            except Exception as e:
                logger.error(f"Не вдалося надіслати дайджест в {chat_id}: {e}")