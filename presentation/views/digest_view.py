# presentation/views/digest_view.py
from aiogram.types import InlineKeyboardMarkup
from presentation.keyboards.main_menu import get_main_menu_kb

async def render_main_digest() -> tuple[str, InlineKeyboardMarkup]:
    from application.container import Container

    service = Container.get().digest
    text = await service.generate_yesterday_digest()

    return text, get_main_menu_kb()