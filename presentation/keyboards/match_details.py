from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardMarkup

from data.icons import ICONS

def get_match_details_kb(fixture_id: int) -> InlineKeyboardMarkup:
    """Клавіатура для детального перегляду матчу"""
    builder = InlineKeyboardBuilder()
    builder.button(text=f"{ICONS['lineup']} Склади команд", callback_data=f"lineups:{fixture_id}")
    builder.button(text=f"{ICONS['ball']} Події матчу", callback_data=f"events:{fixture_id}")
    builder.button(text=f"{ICONS['stats']} Статистика", callback_data=f"stats:{fixture_id}")
    builder.button(text=f"{ICONS['back']} Назад до матчів", callback_data="to_matches")
    builder.adjust(1)
    return builder.as_markup()

def get_lineups_kb(fixture_id: int, home: str, away: str) -> InlineKeyboardMarkup:
    """Вибір команди для перегляду складу"""
    builder = InlineKeyboardBuilder()
    builder.button(text=f"👕 {home}", callback_data=f"lineup:home:{fixture_id}")
    builder.button(text=f"👕 {away}", callback_data=f"lineup:away:{fixture_id}")
    builder.button(text=f"{ICONS['back']} Назад", callback_data=f"match_detail:{fixture_id}")
    builder.adjust(1)
    return builder.as_markup()
