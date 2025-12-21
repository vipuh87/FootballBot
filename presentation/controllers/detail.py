# presentation/controllers/detail.py
from aiogram import Router
from aiogram.types import CallbackQuery
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext

from application.container import Container
from presentation.states import BotStates
from presentation.views.match_details import render_match_details
from presentation.views.events import render_events
from presentation.views.statistics import render_stats
from presentation.views.keyboards import match_detail_keyboard
from data.icons import ICONS
from utils.common import safe_edit

router = Router()


@router.callback_query(lambda c: c.data.startswith("detail:"))
async def cb_detail(c: CallbackQuery, state: FSMContext):
    fid = int(c.data.split(":")[1])

    repo = Container.get().repo
    match = await repo.find_match_by_id(fid)

    if not match:
        await c.answer(f"{ICONS['cancel']} Матч не знайдено", show_alert=True)
        return

    # Зберігаємо day_offset для "назад"
    previous_data = await state.get_data()
    day_offset = previous_data.get("day_offset", 0)

    await state.set_state(BotStates.match_detail)
    await state.update_data(fixture_id=fid, day_offset=day_offset)

    text, _ = render_match_details(match)
    kb = match_detail_keyboard(fid)  # З keyboards.py

    await safe_edit(c, text, kb, parse_mode="HTML")


@router.callback_query(lambda c: c.data.startswith("events:"), StateFilter(BotStates.match_detail))
async def cb_events(c: CallbackQuery, state: FSMContext):
    fid = int(c.data.split(":")[1])

    repo = Container.get().repo
    match = await repo.find_match_by_id(fid)
    details_service = Container.get().match_details

    if not match:
        await c.answer(f"{ICONS['cancel']} Матч не знайдено", show_alert=True)
        return

    # Оновлюємо деталі, якщо матч завершений і даних немає
    match = await details_service.ensure_details(match)

    if not match.events:
        await c.answer(
            f"{ICONS['info']} Події ще не завантажені. Спробуй оновити день або зачекай ранкового оновлення",
            show_alert=True
        )
        return

    await state.set_state(BotStates.events)
    await state.update_data(fixture_id=fid)

    text, kb = render_events(match.events, fid)
    await safe_edit(c, text[:3900], kb, parse_mode="HTML")

@router.callback_query(lambda c: c.data.startswith("stats:"), StateFilter(BotStates.match_detail))
async def cb_stats(c: CallbackQuery, state: FSMContext):
    fid = int(c.data.split(":")[1])

    repo = Container.get().repo
    details_service = Container.get().match_details
    match = await repo.find_match_by_id(fid)

    if not match:
        await c.answer(f"{ICONS['cancel']} Матч не знайдено", show_alert=True)
        return

    if match.status not in ("FT", "AET", "PEN"):
        await c.answer(f"{ICONS['stats']} Статистика доступна після завершення", show_alert=True)
        return

    match = await details_service.ensure_details(match)

    if not match.statistics:
        await c.answer("❌ Статистика ще не завантажена", show_alert=True)
        return

    await state.set_state(BotStates.stats)
    await state.update_data(fixture_id=fid)

    text, kb = render_stats(match.statistics, fid)
    await safe_edit(c, text[:3900], kb, parse_mode="HTML")