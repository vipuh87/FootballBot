# presentation/controllers/players.py
from aiogram import Router
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from data.selected_teams import TEAMS
from presentation.states import BotStates
from presentation.views.players import render_players
from utils.common import safe_edit


router = Router()


@router.callback_query(lambda c: c.data == "players")
async def cb_players(c: CallbackQuery, state: FSMContext):
    # render_players вже повертає правильну кнопку "Назад до новин"
    text, kb = render_players(TEAMS.items())

    await state.set_state(BotStates.players)
    await safe_edit(c, text, kb, parse_mode="HTML")
    await c.answer()