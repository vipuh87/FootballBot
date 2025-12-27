from datetime import date, timedelta
from aiogram import Router, F
from aiogram.types import CallbackQuery
from application.container import Container
from aiogram.fsm.context import FSMContext

# Views для рендеру тексту
from presentation.views.match_list import render_matches_list
from presentation.views.match_details import render_match_details
from presentation.states import BotStates
from utils.common import safe_edit

router = Router(name="matches_router")

# =============== НАВІГАЦІЯ ПО ДНЯХ (з табами) ===============
async def _render_matches_day(target_day: date, offset: int):
    repo = Container.get().repo
    matches = await repo.list_matches_for_day(target_day)

    text, kb = await render_matches_list(matches, target_day, current_day_offset=offset)

    return text, kb


@router.callback_query(lambda c: c.data.startswith("day:"))
async def cb_day(c: CallbackQuery, state: FSMContext):
    offset = int(c.data.split(":")[1])
    target_day = date.today() + timedelta(days=offset)

    text, kb = await _render_matches_day(target_day, offset)

    await state.set_state(BotStates.day_view)
    await state.update_data(day_offset=offset)

    await safe_edit(c, text, kb, parse_mode="HTML")

# =============== ПЕРЕХІД ДО ДЕТАЛЕЙ МАТЧУ ===============
@router.callback_query(F.data.startswith("match_detail:"))
async def select_match(callback: CallbackQuery):
    fixture_id = int(callback.data.split(":")[1])

    repo = Container.get().repo
    match = await repo.find_match_by_id(fixture_id)

    if not match:
        await callback.answer("Матч не знайдено 😔", show_alert=True)
        return

    # Завантажуємо деталі, якщо їх ще немає (lineups завжди, events+stats для завершених)
    details_service = Container.get().match_details
    match = await details_service.ensure_details(match)

    # Рендеримо базові деталі матчу
    text, kb = render_match_details(match)

    await callback.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
    await callback.answer()
