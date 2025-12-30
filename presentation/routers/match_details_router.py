from aiogram import Router, F
from aiogram.types import CallbackQuery

from application.container import Container
from application.services.lineup_service import get_home_lineup, get_away_lineup

# Views для рендеру
from presentation.views.events import render_events
from presentation.views.statistics import render_stats
from presentation.views.match_details import render_match_details
from presentation.keyboards.match_details import get_lineups_kb
from presentation.views.lineup import render_lineup

# Keyboards
from presentation.keyboards.match_details import get_match_details_kb


router = Router(name="match_detail_router")


# Події матчу
@router.callback_query(F.data.startswith("events:"))
async def show_events(callback: CallbackQuery):
    fixture_id = int(callback.data.split(":")[1])

    repo = Container.get().repo
    match = await repo.find_match_by_id(fixture_id)

    if not match or not match.events:
        await callback.answer("Події ще не доступні або матч не завершений", show_alert=True)
        return

    text, kb = render_events(match.events, fixture_id)

    await callback.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
    await callback.answer()


# Статистика матчу
@router.callback_query(F.data.startswith("stats:"))
async def show_statistics(callback: CallbackQuery):
    fixture_id = int(callback.data.split(":")[1])

    repo = Container.get().repo
    match = await repo.find_match_by_id(fixture_id)

    if not match or not match.statistics:
        await callback.answer("Статистика ще не доступна", show_alert=True)
        return

    text, kb = render_stats(match.statistics, fixture_id)

    await callback.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
    await callback.answer()

#Склади команд
@router.callback_query(F.data.startswith("lineups:"))
async def show_lineups_overview(callback: CallbackQuery):
    fixture_id = int(callback.data.split(":")[1])

    repo = Container.get().repo
    match = await repo.find_match_by_id(fixture_id)

    if not match or not match.lineups:
        await callback.answer("Склади ще не доступні", show_alert=True)
        return

    text = "Оберіть команду для перегляду складу:"

    await callback.message.edit_text(text, reply_markup=get_lineups_kb(fixture_id, match.home, match.away), parse_mode="HTML")
    await callback.answer()

@router.callback_query(F.data.startswith("lineup:home:") | F.data.startswith("lineup:away:"))
async def show_team_lineup(callback: CallbackQuery):
    parts = callback.data.split(":")
    side = parts[1]  # "home" або "away"
    fixture_id = int(parts[2])

    repo = Container.get().repo
    match = await repo.find_match_by_id(fixture_id)

    if not match or not match.lineups:
        await callback.answer("Склади ще не доступні", show_alert=True)
        return

    lineup_data = get_home_lineup(match) if side == "home" else get_away_lineup(match)
    if not lineup_data:
        await callback.answer(f"Склад {side} команди недоступний", show_alert=True)
        return

    result = render_lineup(lineup_data, fixture_id)
    text, kb = result if isinstance(result, tuple) else (result, get_match_details_kb(fixture_id))

    await callback.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
    await callback.answer()

# Універсальний back до базових деталей матчу
@router.callback_query(F.data.startswith("detail_") | F.data == "back_to_detail")
async def back_to_match_details(callback: CallbackQuery):
    fixture_id = int(callback.data.split("_")[1]) if "_" in callback.data else None
    # Якщо fixture_id не в data — можна витягнути з попереднього контексту (FSM або cache), але простіше передавати в data

    match = await Container.get().repo.find_match_by_id(fixture_id)
    text = render_match_details(match)
    kb = get_match_details_kb(match)

    await callback.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
    await callback.answer()