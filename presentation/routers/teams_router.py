from aiogram import Router, F
from aiogram.types import CallbackQuery

from application.services.team_service import get_all_teams

from presentation.views.teams import render_teams

router = Router(name="teams_router")


# Вхід у розділ "Команди" з головного меню (callback з кнопки)
@router.callback_query(F.data == "teams")
async def show_teams_list(callback: CallbackQuery):
    teams = get_all_teams()

    if not teams:
        await callback.message.edit_text("Відстежувані команди не налаштовані.")
        await callback.answer()
        return

    text, kb = render_teams(teams)

    await callback.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
    await callback.answer()