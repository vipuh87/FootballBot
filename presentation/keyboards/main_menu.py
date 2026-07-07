from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


def get_main_menu_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="Команди", callback_data="teams")
    builder.button(text="Матчі", callback_data="to_matches")
    builder.button(text="Гравці", callback_data="players")
    builder.button(text="🏆 Прогнози ЧС-2026", callback_data="pred:menu")
    builder.button(text="Оновити", callback_data="refresh")
    builder.adjust(3, 1, 1)
    return builder.as_markup()


def get_single_back_keyboard(callback_data: str = "nav_back") -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="⬅️ Назад", callback_data=callback_data)
    return builder.as_markup()
