from aiogram import Router, F
from aiogram.types import CallbackQuery

from presentation.views.players import render_players
from application.services.team_service import get_all_teams

router = Router(name="players_router")


@router.callback_query(F.data.startswith("players"))
async def show_players(callback: CallbackQuery):
    teams = get_all_teams()
    text, kb = render_players(teams)
    await callback.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
    await callback.answer()
