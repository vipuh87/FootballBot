# presentation/routers/lineups_router.py

from aiogram import Router, F
from aiogram.types import CallbackQuery

from application.container import Container

# View для рендеру одного складу (домашній або гостьовий)
from presentation.views.lineup import render_lineup  # приймає lineup_data (dict однієї команди)

# Keyboard з деталей матчу (має кнопку back)
from presentation.keyboards.match_details import get_match_details_kb

# Якщо є окрема клавіатура тільки для складів — імпортуй і використовуй

router = Router(name="lineups_router")


# Вхід у склади домашньої команди (кнопка з префіксом, наприклад "lineup_home_")
@router.callback_query(F.data.startswith("lineup_home_"))
async def show_home_lineup(callback: CallbackQuery):
    fixture_id = int(callback.data.split("_")[2])  # підправ, якщо префікс інший (наприклад, "home_lineup_")

    repo = Container.get().repo
    match = await repo.find_match_by_id(fixture_id)

    if not match or not match.lineups:
        await callback.answer("Склад недоступний", show_alert=True)
        return

    # Витягуємо lineup домашньої команди
    home_lineup = next((l for l in match.lineups if l["team"]["id"] == match.home_id), None)
    if not home_lineup:
        await callback.answer("Склад домашньої команди недоступний", show_alert=True)
        return

    text = render_lineup(home_lineup)  # ← правильний формат: передаємо dict однієї команди
    kb = get_match_details_kb(match.fixture_id)  # back до деталей матчу

    await callback.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
    await callback.answer()


# Вхід у склади гостьової команди
@router.callback_query(F.data.startswith("lineup_away_"))
async def show_away_lineup(callback: CallbackQuery):
    fixture_id = int(callback.data.split("_")[2])

    repo = Container.get().repo
    match = await repo.find_match_by_id(fixture_id)

    if not match or not match.lineups:
        await callback.answer("Склад недоступний", show_alert=True)
        return

    away_lineup = next((l for l in match.lineups if l["team"]["id"] == match.away_id), None)
    if not away_lineup:
        await callback.answer("Склад гостьової команди недоступний", show_alert=True)
        return

    text = render_lineup(away_lineup)
    kb = get_match_details_kb(match.fixture_id)

    await callback.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
    await callback.answer()


# Якщо в тебе є одна кнопка "Склади" і потім вибір home/away — можеш додати оглядовий хендлер
# @router.callback_query(F.data.startswith("lineups_"))
# async def lineups_overview(callback: CallbackQuery):
#     # Показ кнопок home/away + back
#     pass