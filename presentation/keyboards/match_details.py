from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardMarkup

from data.icons import ICONS

def get_match_details_kb(fixture_id: int) -> InlineKeyboardMarkup:
    """Клавіатура для детального перегляду матчу"""
    builder = InlineKeyboardBuilder()
    builder.button(text=f"{ICONS['lineup']} Склади команд", callback_data=f"lineups:{fixture_id}")
    builder.button(text=f"{ICONS['ball']} Події матчу", callback_data=f"events:{fixture_id}")
    builder.button(text=f"{ICONS['stats']} Статистика", callback_data=f"stats:{fixture_id}")
    builder.button(text=f"{ICONS['back']} Назад до списку", callback_data="nav_back")
    builder.adjust(1)
    return builder.as_markup()

def get_lineups_kb(fixture_id: int, team1: str, team2: str) -> InlineKeyboardMarkup:
    """Вибір команди для перегляду складу"""
    builder = InlineKeyboardBuilder()
    builder.button(text=f"👕 {team1}", callback_data=f"lineup_team1:{fixture_id}")
    builder.button(text=f"👕 {team2}", callback_data=f"lineup_team2:{fixture_id}")
    builder.button(text=f"{ICONS['back']} Назад", callback_data="nav_back")
    builder.adjust(1)
    return builder.as_markup()
