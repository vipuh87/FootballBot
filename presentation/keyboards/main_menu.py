from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from data.icons import ICONS


def get_main_menu_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="Команди", callback_data="teams")
    builder.button(text="Матчі", callback_data="to_matches")
    builder.button(text="Гравці", callback_data="players")
    builder.button(text="Оновити", callback_data="refresh")
    builder.adjust(3,1)
    return builder.as_markup()

def get_single_back_keyboard(callback_data: str = "nav_back") -> InlineKeyboardMarkup:
    """Універсальна кнопка 'Назад'"""
    builder = InlineKeyboardBuilder()
    builder.button(text="⬅️ Назад", callback_data=callback_data)
    return builder.as_markup()