from pathlib import Path

from aiogram.exceptions import TelegramBadRequest
from aiogram.types import CallbackQuery


REM_PATH = Path("data/reminders.json")


async def safe_edit(c: CallbackQuery, text: str, kb=None, parse_mode: str = None):
    try:
        await c.message.edit_text(text, reply_markup=kb, parse_mode=parse_mode)
    except Exception as exc:
        if "message is not modified" in str(exc).lower():
            await safe_answer(c)
            return

        print(f"Error editing message: {exc}")
        await c.message.answer(text, reply_markup=kb, parse_mode=parse_mode)

    await safe_answer(c)


async def safe_answer(c: CallbackQuery):
    try:
        await c.answer()
    except TelegramBadRequest as exc:
        message = str(exc).lower()
        if "query is too old" not in message and "query id is invalid" not in message:
            raise
