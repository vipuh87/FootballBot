# presentation/controllers/teams.py
from aiogram import Router
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from application.services.team_service import get_all_teams
from presentation.states import BotStates
from presentation.views.teams import render_teams
from utils.common import safe_edit


router = Router()


@router.callback_query(lambda c: c.data == "teams")
async def cb_teams(c: CallbackQuery, state: FSMContext):
    # render_teams вже повертає правильну кнопку "Назад до новин"
    text, kb = render_teams(get_all_teams())

    await state.set_state(BotStates.teams)
    await safe_edit(c, text, kb, parse_mode="HTML")
    await c.answer()