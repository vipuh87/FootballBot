from datetime import date, timedelta

from aiogram import Router
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext

from application.container import Container
from presentation.states import BotStates
from presentation.views.match_list import render_matches_list
from presentation.views.digest_view import render_main_digest
from utils.common import safe_edit

router = Router()


# =============== ГОЛОВНА — ДАЙДЖЕСТ ===============
@router.message(CommandStart())
@router.callback_query(lambda c: c.data == "back_to_digest")
async def show_digest(event: Message | CallbackQuery, state: FSMContext):
    text, kb = await render_main_digest()

    await state.clear()  # Очищаємо стан, бо ми на головній

    if isinstance(event, Message):
        await event.answer(text, reply_markup=kb, parse_mode="HTML")
    else:
        await safe_edit(event, text, kb, parse_mode="HTML")


# =============== ПЕРЕХІД ДО МАТЧІВ ===============
@router.callback_query(lambda c: c.data == "to_matches")
async def to_matches_today(c: CallbackQuery, state: FSMContext):
    repo = Container.get().repo
    today = date.today()
    matches = await repo.list_matches_for_day(today)

    text, kb = await render_matches_list(matches, today, current_day_offset=0)

    await state.set_state(BotStates.day_view)
    await state.update_data(day_offset=0)

    await safe_edit(c, text, kb, parse_mode="HTML")


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


@router.callback_query(lambda c: c.data == "main_menu")
async def cb_main_menu(c: CallbackQuery, state: FSMContext):
    await to_matches_today(c, state)


# =============== РУЧНЕ ОНОВЛЕННЯ ===============
@router.callback_query(lambda c: c.data.startswith("refresh:"))
async def cb_refresh(c: CallbackQuery, state: FSMContext):
    repo = Container.get().repo
    api = Container.get().api
    details_service = Container.get().match_details


    day_str = c.data.split(":")[1]
    day = date.fromisoformat(day_str)

    await c.answer("🔄 Оновлюю дані...")

    try:
        print(f"🔄 MANUAL REFRESH: {day}")
        await repo.refresh_day(day, api)

        # Оновлюємо деталі для всіх матчів дня
        matches = await repo.list_matches_for_day(day)
        for m in matches:
            await details_service.ensure_details(m)

        print(f"✅ REFRESH OK + DETAILS: {day}")
    except Exception as e:
        print(f"❌ REFRESH ERROR {day}:", e)
        await c.answer("❌ Помилка оновлення даних", show_alert=True)
        offset = (day - date.today()).days
        text, kb = await _render_matches_day(day, offset)
        await safe_edit(c, text, kb, parse_mode="HTML")

    # Перезавантажуємо список матчів
    offset = (day - date.today()).days
    text, kb = await _render_matches_day(day, offset)

    await safe_edit(c, text, kb, parse_mode="HTML")