import re

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from application.services.predictions import PredictionService
from application.services.predictions.prediction_service import RULES_TEXT_UA
from presentation.keyboards.predictions import (
    DATES_PER_PAGE,
    champion_teams_kb,
    dates_kb,
    match_prediction_kb,
    matches_menu_kb,
    matches_kb,
    predictions_back_kb,
    predictions_menu_kb,
)
from presentation.states import BotStates
from presentation.views.predictions import (
    render_champion,
    render_dates_page,
    render_match,
    render_matches,
    render_matches_menu,
    render_my_predictions,
    render_prediction_menu,
    render_standings,
    render_tournament_structure,
)
from utils.common import safe_edit

router = Router(name="predictions_router")


def service() -> PredictionService:
    return PredictionService()


@router.callback_query(F.data == "pred:menu")
async def prediction_menu(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    svc = service()
    participant = svc.participants().get(str(callback.from_user.id))
    champion = svc.user_champion_prediction(callback.from_user.id)
    await safe_edit(callback, render_prediction_menu(participant, champion), predictions_menu_kb(), parse_mode="HTML")


@router.callback_query(F.data == "pred:join")
async def join_predictions(callback: CallbackQuery, state: FSMContext):
    svc = service()
    svc.register_participant(callback.from_user, callback.message.chat.id)
    champion = svc.user_champion_prediction(callback.from_user.id)
    if not svc.is_champion_locked():
        await state.set_state(BotStates.prediction_champion)
        await safe_edit(callback, render_champion(champion, svc), champion_teams_kb(svc.world_cup_teams()), parse_mode="HTML")
        await callback.answer("Ти в турнірі. Обери чемпіона.")
        return

    participant = svc.participants().get(str(callback.from_user.id))
    await safe_edit(callback, render_prediction_menu(participant, champion), predictions_menu_kb(), parse_mode="HTML")
    await callback.answer("Ти в турнірі прогнозів!")


@router.callback_query(F.data == "pred:champion")
async def champion_prediction(callback: CallbackQuery, state: FSMContext):
    svc = service()
    champion = svc.user_champion_prediction(callback.from_user.id)
    reply_markup = predictions_back_kb() if svc.is_champion_locked() else champion_teams_kb(svc.world_cup_teams())
    await safe_edit(callback, render_champion(champion, svc), reply_markup, parse_mode="HTML")
    if not svc.is_champion_locked():
        await state.set_state(BotStates.prediction_champion)
    await callback.answer()


@router.callback_query(F.data.startswith("pred:champ_page:"))
async def champion_page(callback: CallbackQuery, state: FSMContext):
    svc = service()
    if svc.is_champion_locked():
        await callback.answer("Прогноз чемпіона вже закрито.", show_alert=True)
        return

    page = int(callback.data.split(":")[2])
    await state.set_state(BotStates.prediction_champion)
    champion = svc.user_champion_prediction(callback.from_user.id)
    await safe_edit(callback, render_champion(champion, svc), champion_teams_kb(svc.world_cup_teams(), page), parse_mode="HTML")
    await callback.answer()


@router.callback_query(F.data.startswith("pred:champ_pick:"))
async def champion_pick(callback: CallbackQuery, state: FSMContext):
    svc = service()
    team_id = int(callback.data.split(":")[2])

    try:
        svc.save_champion_prediction_by_team_id(callback.from_user, callback.message.chat.id, team_id)
    except ValueError as exc:
        await callback.answer(str(exc), show_alert=True)
        return

    await state.clear()
    participant = svc.participants().get(str(callback.from_user.id))
    champion = svc.user_champion_prediction(callback.from_user.id)
    await safe_edit(callback, render_prediction_menu(participant, champion), predictions_menu_kb(), parse_mode="HTML")
    await callback.answer("Прогноз чемпіона збережено")


@router.message(BotStates.prediction_champion)
async def save_champion_prediction(message: Message, state: FSMContext):
    svc = service()
    try:
        svc.save_champion_prediction(message.from_user, message.chat.id, message.text or "")
    except ValueError as exc:
        await message.answer(str(exc), reply_markup=predictions_back_kb())
        return

    await state.clear()
    await message.answer("✅ Прогноз чемпіона збережено", reply_markup=predictions_back_kb())


@router.callback_query(F.data == "pred:tournament")
async def prediction_tournament(callback: CallbackQuery):
    svc = service()
    await safe_edit(
        callback,
        render_tournament_structure(svc.matches()),
        predictions_back_kb(),
        parse_mode="HTML",
    )


@router.callback_query(F.data == "pred:matches")
async def prediction_matches(callback: CallbackQuery):
    svc = service()
    await safe_edit(
        callback,
        render_matches_menu(len(svc.matches()), len(svc.match_dates())),
        matches_menu_kb(),
        parse_mode="HTML",
    )


@router.callback_query(F.data == "pred:upcoming")
async def prediction_upcoming_matches(callback: CallbackQuery):
    svc = service()
    matches = svc.upcoming_matches()
    await safe_edit(
        callback,
        render_matches(matches, svc, callback.from_user.id, title="⏭ Найближчі матчі"),
        matches_kb(matches, back_callback="pred:matches"),
        parse_mode="HTML",
    )


@router.callback_query(F.data.startswith("pred:dates:"))
async def prediction_dates(callback: CallbackQuery):
    page = int(callback.data.split(":")[2])
    svc = service()
    dates = svc.match_dates()
    await safe_edit(
        callback,
        render_dates_page(dates, page, DATES_PER_PAGE),
        dates_kb(dates, page),
        parse_mode="HTML",
    )


@router.callback_query(F.data.startswith("pred:date:"))
async def prediction_matches_by_date(callback: CallbackQuery):
    day = callback.data.split(":")[2]
    svc = service()
    matches = svc.matches_by_date(day)
    await safe_edit(
        callback,
        render_matches(matches, svc, callback.from_user.id, title=f"📅 Матчі {day}"),
        matches_kb(matches, back_callback="pred:dates:0"),
        parse_mode="HTML",
    )


@router.callback_query(F.data.startswith("pred:match:"))
async def prediction_match(callback: CallbackQuery):
    fixture_id = int(callback.data.split(":")[2])
    svc = service()
    match = svc.find_match(fixture_id)
    if not match:
        await callback.answer("Матч не знайдено", show_alert=True)
        return

    prediction = svc.user_prediction(callback.from_user.id, fixture_id)
    await safe_edit(
        callback,
        render_match(match, svc, prediction),
        match_prediction_kb(fixture_id, svc.is_locked(match) or not svc.is_match_resolved(match)),
        parse_mode="HTML",
    )


@router.callback_query(F.data.startswith("pred:score:"))
async def save_quick_prediction(callback: CallbackQuery):
    _, _, fixture_id, home_score, away_score = callback.data.split(":")
    svc = service()
    try:
        svc.save_prediction(
            callback.from_user,
            callback.message.chat.id,
            int(fixture_id),
            int(home_score),
            int(away_score),
        )
    except ValueError as exc:
        await callback.answer(str(exc), show_alert=True)
        return

    match = svc.find_match(int(fixture_id))
    prediction = svc.user_prediction(callback.from_user.id, int(fixture_id))
    await safe_edit(
        callback,
        render_match(match, svc, prediction),
        match_prediction_kb(int(fixture_id), svc.is_locked(match) or not svc.is_match_resolved(match)),
        parse_mode="HTML",
    )
    await callback.answer("Прогноз збережено")


@router.callback_query(F.data.startswith("pred:manual:"))
async def ask_manual_prediction(callback: CallbackQuery, state: FSMContext):
    fixture_id = int(callback.data.split(":")[2])
    svc = service()
    match = svc.find_match(fixture_id)
    if not match:
        await callback.answer("Матч не знайдено", show_alert=True)
        return
    if svc.is_locked(match):
        await callback.answer("Прийом прогнозів на цей матч уже закрито.", show_alert=True)
        return
    if not svc.is_match_resolved(match):
        await callback.answer("Команди цього матчу ще не визначені.", show_alert=True)
        return

    await state.set_state(BotStates.prediction_manual_score)
    print(
        "STATE SET",
        callback.from_user.id,
        callback.message.chat.id
    )
    await state.update_data(prediction_fixture_id=fixture_id)
    await callback.message.answer("👇 Відповіддю на це повідомлення введи рахунок у форматі 2:1")
    await callback.answer()


@router.message(BotStates.prediction_manual_score)
async def save_manual_prediction(message: Message, state: FSMContext):
    print(
        "HANDLER ENTERED",
        message.from_user.id,
        message.chat.id,
        message.text,
    )
    score_match = re.fullmatch(r"\s*(\d{1,2})\s*[:\-]\s*(\d{1,2})\s*", message.text or "")
    if not score_match:
        await message.answer("Не бачу рахунок. Введи у форматі 2:1")
        return

    data = await state.get_data()
    fixture_id = int(data["prediction_fixture_id"])
    svc = service()
    try:
        svc.save_prediction(
            message.from_user,
            message.chat.id,
            fixture_id,
            int(score_match.group(1)),
            int(score_match.group(2)),
        )
    except ValueError as exc:
        await message.answer(str(exc))
        return

    await state.clear()
    await message.answer("✅ Прогноз збережено", reply_markup=predictions_back_kb())


@router.callback_query(F.data == "pred:mine")
async def my_predictions(callback: CallbackQuery):
    svc = service()
    text = render_my_predictions(
        svc.matches(),
        svc.user_predictions(callback.from_user.id),
        svc.user_champion_prediction(callback.from_user.id),
    )
    await safe_edit(callback, text, predictions_back_kb(), parse_mode="HTML")


@router.callback_query(F.data == "pred:standings")
async def prediction_standings(callback: CallbackQuery):
    svc = service()
    await safe_edit(
        callback,
        render_standings(svc.standings(), current_user_id=callback.from_user.id),
        predictions_back_kb(),
        parse_mode="HTML",
    )


@router.callback_query(F.data == "pred:rules")
async def prediction_rules(callback: CallbackQuery):
    await safe_edit(callback, RULES_TEXT_UA, predictions_back_kb(), parse_mode="HTML")
