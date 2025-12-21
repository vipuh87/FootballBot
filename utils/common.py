from pathlib import Path
from aiogram.types import CallbackQuery

REM_PATH = Path("data/reminders.json")

async def safe_edit(c: CallbackQuery, text: str, kb=None, parse_mode: str = None):
    try:
        await c.message.edit_text(text, reply_markup=kb, parse_mode=parse_mode)
    except Exception as e:
        if "message is not modified" in str(e).lower():
            await c.answer()  # просто підтверджуємо, щоб кнопка не "зависла"
            return
        print(f"Error editing message: {e}")
        # fallback — нове повідомлення
        await c.message.answer(text, reply_markup=kb, parse_mode=parse_mode)
