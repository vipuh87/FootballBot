# presentation/controllers/navigation.py
from aiogram import Router
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from datetime import date, timedelta

from application.container import Container
from presentation.states import BotStates
from presentation.views.match_list import render_matches_list
from presentation.views.match_details import render_match_details  # ← ДОДАЙ цей імпорт
from presentation.views.digest_view import render_main_digest
from utils.common import safe_edit
from data.icons import ICONS

router = Router()


@router.callback_query(lambda c: c.data == "nav_back")
async def cb_nav_back(c: CallbackQuery, state: FSMContext):
    repo = Container.get().repo

    current_state = await state.get_state()
    if current_state is None:
        # Якщо стан втрачено — повертаємо до дайджесту
        text, kb = await render_main_digest()
        await state.clear()
        await safe_edit(c, text, kb, parse_mode="HTML")
        return

    data = await state.get_data()
    fid = data.get("fixture_id")
    day_offset = data.get("day_offset", 0)
    target_day = date.today() + timedelta(days=day_offset)

    # 1. З меню складів або конкретного складу → назад в деталі матчу
    if current_state in (BotStates.lineups_menu, BotStates.lineup_team):
        if not fid:
            # fallback в список
            matches = await repo.list_matches_for_day(target_day)
            text, kb = await render_matches_list(matches, target_day, current_day_offset=day_offset)
            await state.set_state(BotStates.day_view)
            await state.update_data(day_offset=day_offset)
            await safe_edit(c, text, kb, parse_mode="HTML")
            return

        match = await repo.find_match_by_id(fid)
        if not match:
            await c.answer(f"{ICONS['cancel']} Матч не знайдено", show_alert=True)
            return

        text, kb = render_match_details(match)
        await state.set_state(BotStates.match_detail)
        await state.update_data(fixture_id=fid, day_offset=day_offset)

        await safe_edit(c, text, kb, parse_mode="HTML")
        return

    # 2. З подій або статистики → назад в деталі матчу
    if current_state in (BotStates.events, BotStates.stats):
        if not fid:
            # fallback
            matches = await repo.list_matches_for_day(target_day)
            text, kb = await render_matches_list(matches, target_day, current_day_offset=day_offset)
            await state.set_state(BotStates.day_view)
            await state.update_data(day_offset=day_offset)
            await safe_edit(c, text, kb, parse_mode="HTML")
            return

        match = await repo.find_match_by_id(fid)
        if not match:
            await c.answer(f"{ICONS['cancel']} Матч не знайдено", show_alert=True)
            return

        text, kb = render_match_details(match)
        await state.set_state(BotStates.match_detail)
        await state.update_data(fixture_id=fid, day_offset=day_offset)

        await safe_edit(c, text, kb, parse_mode="HTML")
        return

    # 3. З деталей матчу → назад до списку матчів
    if current_state == BotStates.match_detail:
        matches = await repo.list_matches_for_day(target_day)
        text, kb = await render_matches_list(matches, target_day, current_day_offset=day_offset)

        await state.set_state(BotStates.day_view)
        await state.update_data(day_offset=day_offset)

        await safe_edit(c, text, kb, parse_mode="HTML")
        return

    # 4. Зі списку матчів → назад до дайджесту
    if current_state == BotStates.day_view:
        text, kb = await render_main_digest()
        await state.clear()
        await safe_edit(c, text, kb, parse_mode="HTML")
        return

    # 5. З інших розділів (teams, players) → дайджест
    if current_state in (BotStates.teams, BotStates.players):
        text, kb = await render_main_digest()
        await state.clear()
        await safe_edit(c, text, kb, parse_mode="HTML")
        return

    # Будь-який інший стан → дайджест
    text, kb = await render_main_digest()
    await state.clear()
    await safe_edit(c, text, kb, parse_mode="HTML")