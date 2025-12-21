from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from datetime import date

from data.icons import ICONS
from domain.models.match import Match

def get_day_kb(day: date, current_day_offset: int = 0) -> InlineKeyboardMarkup:
    """Клавіатура для списку матчів з табами та кнопкою назад"""
    builder = InlineKeyboardBuilder()

    # Таби: Вчора / Сьогодні / Завтра
    offsets = [-1, 0, 1]
    labels = ["Вчора", "Сьогодні", "Завтра"]
    for offset, label in zip(offsets, labels):
        button_text = f"{ICONS['calendar']} {label}"
        if offset == current_day_offset:
            button_text = f"✅ {button_text}"
        builder.button(text=button_text, callback_data=f"day:{offset}")

    # Кнопка оновлення
    builder.row(
        InlineKeyboardButton(text=f"{ICONS['refresh']} Оновити", callback_data=f"refresh:{day.isoformat()}")
    )

    return builder.as_markup()


def get_match_card_kb(match: Match) -> list[InlineKeyboardButton]:
    """Рядок з кнопкою матчу для вставки в клавіатуру"""
    return [
        InlineKeyboardButton(
            text=f"{ICONS['match']} {match.home} — {match.away}",
            callback_data=f"detail:{match.fixture_id}"
        )
    ]