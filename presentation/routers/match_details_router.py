# presentation/routers/match_detail_router.py

from aiogram import Router, F
from aiogram.types import CallbackQuery

from application.container import Container

# Views для рендеру
from presentation.views.events import render_events
from presentation.views.statistics import render_stats
from presentation.views.lineup import render_lineup
from presentation.views.players import render_players
from presentation.views.match_details import render_match_details

# Keyboards
from presentation.keyboards.match_details import get_match_details_kb

# Якщо є окремі клавіатури для подій/статистики — імпортуй їх тут

router = Router(name="match_detail_router")


# Події матчу
@router.callback_query(F.data.startswith("events_"))
async def show_events(callback: CallbackQuery):
    fixture_id = int(callback.data.split("_")[1])

    repo = Container.get().repo
    match = await repo.find_match_by_id(fixture_id)

    if not match or not match.events:
        await callback.answer("Події ще не доступні або матч не завершений", show_alert=True)
        return

    text = render_events(match)  # твоя view-функція для подій
    # Клавіатура з back до деталей
    kb = get_match_details_kb(match)  # або окрема з кнопкою "Назад до деталей"

    await callback.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
    await callback.answer()


# Статистика матчу
@router.callback_query(F.data.startswith("stats_"))
async def show_statistics(callback: CallbackQuery):
    fixture_id = int(callback.data.split("_")[1])

    repo = Container.get().repo
    match = await repo.find_match_by_id(fixture_id)

    if not match or not match.statistics:
        await callback.answer("Статистика ще не доступна", show_alert=True)
        return

    text = render_stats(match)
    kb = get_match_details_kb(match)

    await callback.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
    await callback.answer()


# Склади — головний вхід (можливо кнопка "Склади")
@router.callback_query(F.data.startswith("lineups_"))
async def show_lineups_overview(callback: CallbackQuery):
    fixture_id = int(callback.data.split("_")[1])

    repo = Container.get().repo
    match = await repo.find_match_by_id(fixture_id)

    if not match or not match.lineups:
        await callback.answer("Склади ще не доступні", show_alert=True)
        return

    # Можна показати короткий огляд обох складів або кнопки на home/away
    text = "Оберіть команду для перегляду складу:"
    # kb з кнопками "🏠 {home} склад", "✈️ {away} склад", back
    # Або відразу показати обидва — залежить від твоєї view

    await callback.message.edit_text(text, reply_markup=some_lineups_kb(match))
    await callback.answer()


# Склад домашньої команди
@router.callback_query(F.data.startswith("lineup_home_"))
async def show_home_lineup(callback: CallbackQuery):
    fixture_id = int(callback.data.split("_")[2])
    # логіка аналогічна, рендер render_lineup(match, home=True)
    pass  # заповни за аналогією


# Склад гостьової команди
@router.callback_query(F.data.startswith("lineup_away_"))
async def show_away_lineup(callback: CallbackQuery):
    pass


# Українські гравці в матчі (якщо є окрема кнопка)
@router.callback_query(F.data.startswith("ukr_players_"))
async def show_ukrainian_players(callback: CallbackQuery):
    fixture_id = int(callback.data.split("_")[2])

    match = await Container.get().repo.find_match_by_id(fixture_id)
    ua_info = await Container.get().players_service.get_ukrainian_players_for_match(match)  # або твій сервіс

    text = render_ukrainian_players(match, ua_info)  # твоя view
    kb = get_match_details_kb(match)

    await callback.message.edit_text(text, reply_markup=kb)
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