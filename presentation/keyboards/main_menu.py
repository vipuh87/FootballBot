from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from data.icons import ICONS


def get_main_menu_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="Команди", callback_data="teams")
    builder.button(text="Матчі", callback_data="to_matches")
    builder.button(text="Гравці", callback_data="players")
    builder.adjust(3)
    return builder.as_markup()

def get_back_to_digest_button() -> InlineKeyboardButton:
    return InlineKeyboardButton(text=f"{ICONS['back']} Назад до новин", callback_data="back_to_digest")

def get_single_back_keyboard(callback_data: str = "nav_back") -> InlineKeyboardMarkup:
    """Універсальна кнопка 'Назад'"""
    builder = InlineKeyboardBuilder()
    builder.button(text="⬅️ Назад", callback_data=callback_data)
    return builder.as_markup()