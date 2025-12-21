# presentation/controllers/lineups.py
from datetime import datetime, timezone

from aiogram import Router
from aiogram.types import CallbackQuery
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext

from application.container import Container
from presentation.states import BotStates
from presentation.views.lineup import render_lineup_menu, render_lineup
from utils.common import safe_edit
from data.icons import ICONS

router = Router()


@router.callback_query(lambda c: c.data.startswith("lineups:"), StateFilter(BotStates.match_detail))
async def cb_lineups_menu(c: CallbackQuery, state: FSMContext):
    fid = int(c.data.split(":")[1])

    repo = Container.get().repo
    api = Container.get().api
    details_service = Container.get().match_details  # ← Додаємо

    match = await repo.find_match_by_id(fid)

    if not match:
        await c.answer(f"{ICONS['cancel']} Матч не знайдено", show_alert=True)
        return

    # Оновлюємо деталі (lineups завантажаться, якщо немає)
    match = await details_service.ensure_details(match)

    kickoff_dt = datetime.fromisoformat(match.date_utc.replace("Z", "+00:00"))
    now = datetime.now(timezone.utc)
    diff_minutes = (kickoff_dt - now).total_seconds() / 60

    if diff_minutes > 30:
        await c.answer(f"{ICONS['shirt']} Склади зʼявляються приблизно за 30 хв до матчу", show_alert=True)
        return

    if not match.lineups:  # Тепер це малоймовірно, але на всяк випадок
        await c.answer(f"{ICONS['cancel']} На жаль, склади не надані", show_alert=True)
        return

    # Зберігаємо day_offset
    previous_data = await state.get_data()
    day_offset = previous_data.get("day_offset", 0)
    await state.update_data(fixture_id=fid, day_offset=day_offset)

    await state.set_state(BotStates.lineups_menu)

    home = match.home
    away = match.away

    text, kb = render_lineup_menu(fid, home, away)
    await safe_edit(c, text, kb, parse_mode="HTML")


@router.callback_query(lambda c: c.data.startswith("lineup_team"))
async def cb_lineup_team(c: CallbackQuery, state: FSMContext):
    parts = c.data.split(":")
    if len(parts) != 2:
        await c.answer("Помилка обробки", show_alert=True)
        return

    team_key = parts[0]
    fid = int(parts[1])

    repo = Container.get().repo
    details_service = Container.get().match_details  # ← Додаємо

    match = await repo.find_match_by_id(fid)

    if not match:
        await c.answer(f"{ICONS['cancel']} Матч не знайдено", show_alert=True)
        return

    # Оновлюємо деталі (lineups)
    match = await details_service.ensure_details(match)

    if not match.lineups or len(match.lineups) < 2:
        await c.answer(f"{ICONS['cancel']} На жаль, склади не надані", show_alert=True)
        return

    if team_key == "lineup_team1":
        team_data = match.lineups[0]
    elif team_key == "lineup_team2":
        team_data = match.lineups[1]
    else:
        await c.answer("Невідома команда", show_alert=True)
        return

    team_name = team_data["team"]["name"]
    coach = team_data.get("coach", {}).get("name", "—")
    start_xi = team_data.get("startXI", [])
    subs = team_data.get("substitutes", [])

    previous_data = await state.get_data()
    day_offset = previous_data.get("day_offset", 0)
    await state.update_data(fixture_id=fid, day_offset=day_offset)

    await state.set_state(BotStates.lineup_team)

    text, kb = render_lineup(team_name, coach, start_xi, subs)
    await safe_edit(c, text[:3900], kb, parse_mode="HTML")