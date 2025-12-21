# presentation/views/digest_view.py
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardMarkup

from application.container import Container


async def render_main_digest() -> tuple[str, InlineKeyboardMarkup]:
    service = Container.get().digest
    text = await service.generate_yesterday_digest()

    builder = InlineKeyboardBuilder()
    builder.button(text="Команди", callback_data="teams")
    builder.button(text="До Матчів", callback_data="to_matches")
    builder.button(text="Гравці", callback_data="players")
    builder.adjust(3)

    return text, builder.as_markup()