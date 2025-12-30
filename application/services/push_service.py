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

    def __init__(self, bot: Bot, repo):
        self.bot = bot
        self.repo = repo
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
                kwargs = {
                    "parse_mode": "HTML",
                    "disable_web_page_preview": True,
                    "reply_markup": kb,
                }
                # Додаємо thread_id, якщо він є в конфігурації
                if target.get("thread_id"):
                    kwargs["message_thread_id"] = int(target["thread_id"])

                await self.bot.send_message(
                    chat_id=chat_id,
                    text=text,
                    **kwargs
                )
                await asyncio.sleep(0.1)
            except Exception as e:
                logger.error(f"Не вдалося надіслати дайджест в {chat_id}: {e}")

    async def send_announcement(self, text: str, targets: list = None):
        """
        Надсилає ручне оголошення в вказані targets (або всі push_targets за замовчуванням)
        """
        if not text.strip():
            print("❌ Текст оголошення порожній — пропускаю.")
            return

        targets = targets or self.push_targets

        sent_count = 0
        for target in targets:
            try:
                kwargs = {"parse_mode": "HTML"}
                if target.get("thread_id"):
                    kwargs["message_thread_id"] = int(target["thread_id"])

                await self.bot.send_message(
                    chat_id=target["chat_id"],
                    text=text,
                    **kwargs
                )
                sent_count += 1
                await asyncio.sleep(0.1)  # антифлуд
            except Exception as e:
                print(f"❌ Помилка надсилання в {target['chat_id']}: {e}")

        print(f"✅ Оголошення надіслано в {sent_count} з {len(targets)} чатів.")

    async def send_reminder_for_match(self, match):
        """Надсилає нагадування для одного матчу"""
        try:
            ua_info = await get_ukrainian_players_for_match(match)
            text = render_reminder_text(match, ua_info)

            await self._send_plain(text)

            # Зберігаємо, щоб не дублювати (на всяк випадок)
            self.sent[str(match.fixture_id)] = {
                "sent_at": datetime.now(TZ_UKRAINE).isoformat(),
                "match_time_utc": match.date_utc,
            }
            self._save_sent()

            print(f"✅ Нагадування надіслано для матчу {match.fixture_id} ({match.home} — {match.away})")
        except Exception as e:
            print(f"🔥 Помилка надсилання нагадування для {match.fixture_id}: {e}")