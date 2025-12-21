# presentation/views/digest_view.py
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardMarkup

from application.container import Container
from presentation.keyboards.main_menu import get_main_menu_kb

async def render_main_digest() -> tuple[str, InlineKeyboardMarkup]:
    service = Container.get().digest
    text = await service.generate_yesterday_digest()

    return text, get_main_menu_kb()