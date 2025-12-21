# presentation/keyboards.py (або де в тебе цей файл)
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from datetime import date

from data.icons import ICONS
from domain.models.match import Match


def digest_main_keyboard() -> InlineKeyboardMarkup:
    """Клавіатура для головної сторінки (дайджест новин)"""
    builder = InlineKeyboardBuilder()
    builder.button(text="До Матчів", callback_data="to_matches")
    builder.button(text="Команди", callback_data="teams")
    builder.button(text="Гравці", callback_data="players")
    builder.adjust(2, 1)  # 2 кнопки в ряд, остання окремо
    return builder.as_markup()


def matches_day_keyboard(day: date, current_day_offset: int = 0) -> InlineKeyboardMarkup:
    """Клавіатура для списку матчів з табами та кнопкою назад"""
    builder = InlineKeyboardBuilder()

    # Таби: Вчора / Сьогодні / Завтра
    offsets = [-1, 0, 1]
    labels = ["Вчора", "Сьогодні", "Завтра"]
    for offset, label in zip(offsets, labels):
        button_text = f"{ICONS['calendar']} {label}"
        if offset == current_day_offset:
            button_text = f"✅ {button_text}"  # Поточний день з галочкою
        builder.button(text=button_text, callback_data=f"day:{offset}")

    # Кнопка оновлення
    builder.row(
        InlineKeyboardButton(text=f"{ICONS['refresh']} Оновити", callback_data=f"refresh:{day.isoformat()}")
    )

    # Кнопка назад до дайджесту
    builder.row(
        InlineKeyboardButton(text=f"{ICONS['back']} Назад до новин", callback_data="back_to_digest")
    )

    return builder.as_markup()

def match_detail_keyboard(fixture_id: int) -> InlineKeyboardMarkup:
    """Клавіатура для детального перегляду матчу"""
    builder = InlineKeyboardBuilder()
    builder.button(text=f"{ICONS['lineup']} Склади команд", callback_data=f"lineups:{fixture_id}")
    builder.button(text=f"{ICONS['ball']} Події матчу", callback_data=f"events:{fixture_id}")
    builder.button(text=f"{ICONS['stats']} Статистика", callback_data=f"stats:{fixture_id}")
    builder.button(text=f"{ICONS['back']} Назад до списку", callback_data="nav_back")
    builder.adjust(1)  # По одній кнопці в рядку
    return builder.as_markup()


def lineup_team_choice_keyboard(fixture_id: int, team1: str, team2: str) -> InlineKeyboardMarkup:
    """Вибір команди для перегляду складу"""
    builder = InlineKeyboardBuilder()
    builder.button(text=f"👕 {team1}", callback_data=f"lineup_team1:{fixture_id}")
    builder.button(text=f"👕 {team2}", callback_data=f"lineup_team2:{fixture_id}")
    builder.button(text=f"{ICONS['back']} Назад", callback_data="nav_back")
    builder.adjust(1)
    return builder.as_markup()


def single_back_keyboard(callback_data: str = "nav_back") -> InlineKeyboardMarkup:
    """Універсальна кнопка 'Назад'"""
    builder = InlineKeyboardBuilder()
    builder.button(text="⬅️ Назад", callback_data=callback_data)
    return builder.as_markup()


def match_row_button(match: Match) -> list[InlineKeyboardButton]:
    """Рядок з кнопкою матчу для вставки в клавіатуру"""
    return [
        InlineKeyboardButton(
            text=f"{ICONS['match']} {match.home} — {match.away}",
            callback_data=f"detail:{match.fixture_id}"
        )
    ]

def back_to_digest_button() -> InlineKeyboardButton:
    return InlineKeyboardButton(text=f"{ICONS['back']} Назад до новин", callback_data="back_to_digest")