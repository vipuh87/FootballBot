# presentation/routers/navigation_router.py

from aiogram import Router, F
from aiogram.types import CallbackQuery

from application.container import Container

# Views
from presentation.views.match_list import render_matches_list  # для back до списку матчів
from presentation.views.match_details import render_match_details  # для back до деталей матчу

# Keyboards
from presentation.keyboards.main_menu import get_main_menu_kb
from presentation.keyboards.matches import get_day_kb
from presentation.keyboards.match_details import get_match_details_kb

from datetime import date

router = Router(name="navigation_router")


# Повернення в головне меню з будь-якого місця
@router.callback_query(F.data == "main_menu")
async def back_to_main_menu(callback: CallbackQuery):
    text = "🏠 Головне меню"
    kb = get_main_menu_kb()
    await callback.message.edit_text(text, reply_markup=kb)
    await callback.answer()


# Повернення до списку матчів на сьогодні (з деталей, складів тощо)
@router.callback_query(F.data == "back_to_matches")
async def back_to_matches_list(callback: CallbackQuery):
    repo = Container.get().repo
    today = date.today()
    matches = await repo.list_matches_for_day(today)

    if not matches:
        text = "Сьогодні немає матчів за участю відстежуваних команд."
        kb = get_main_menu_kb()
    else:
        text = render_matches_list(matches, day=today)
        kb = get_day_kb(matches)

    await callback.message.edit_text(text, reply_markup=kb)
    await callback.answer()


# Універсальний back до деталей конкретного матчу (кнопка з fixture_id)
@router.callback_query(F.data.startswith("back_to_detail_"))
async def back_to_match_detail(callback: CallbackQuery):
    fixture_id = int(callback.data.split("_")[-1])

    repo = Container.get().repo
    match = await repo.find_match_by_id(fixture_id)

    if not match:
        await callback.answer("Матч не знайдено", show_alert=True)
        return

    # Завантажуємо деталі, якщо потрібно
    details_service = Container.get().match_details
    match = await details_service.ensure_details(match)

    text = render_match_details(match)
    kb = get_match_details_kb(match.fixture_id)

    await callback.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
    await callback.answer()


# Скасування дії (наприклад, при FSM, але можна використовувати і без)
@router.callback_query(F.data == "cancel")
async def cancel_action(callback: CallbackQuery):
    await back_to_main_menu(callback)