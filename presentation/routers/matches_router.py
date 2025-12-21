# presentation/routers/matches_router.py

from datetime import date

from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.filters import Command  # якщо захочеш окрему команду /matches

from application.container import Container

# Views для рендеру тексту
from presentation.views.match_list import render_matches_list
from presentation.views.match_details import render_match_details

# Keyboards
from presentation.keyboards.matches import (  # припускаю назви функцій — підправ якщо інакше
    get_day_kb,
)
from presentation.keyboards.match_details import get_match_details_kb

router = Router(name="matches_router")


# Опціонально: окрема команда для тесту
# @router.message(Command("matches"))
# async def cmd_matches(message: Message):
#     await show_today_matches(message)


# Вхід у розділ матчів з головного меню (callback з кнопки "Матчі" або "Сьогодні")
@router.callback_query(F.data.in_({"matches_today", "matches", "show_matches"}))  # підправ data під свій main_menu
async def enter_matches_section(callback: CallbackQuery):
    await show_today_matches(callback.message)
    await callback.answer()


async def show_today_matches(message: Message | None):
    """Універсальна функція для показу матчів на певний день"""
    repo = Container.get().repo
    today = date.today()

    matches = await repo.list_matches_for_day(today)

    if not matches:
        text = "🕸 Сьогодні немає матчів за участю відстежуваних команд або гравців.\n\nОберіть іншу дату або перейдіть до іншого розділу."
        # Можна додати клавіатуру з вибором дати: вчора / сьогодні / завтра
        kb = None  # або get_date_selection_keyboard()
    else:
        text = render_matches_list(matches, day=today)  # твоя view-функція для списку
        kb = get_day_kb(matches)  # inline-кнопки з callback_data типу "match_12345"

    if message:
        await message.edit_text(text, reply_markup=kb) if message.from_user.is_bot else await message.answer(text, reply_markup=kb)


# Вибір конкретного матчу зі списку
@router.callback_query(F.data.startswith("match_"))
async def select_match(callback: CallbackQuery):
    fixture_id = int(callback.data.split("_")[1])

    repo = Container.get().repo
    match = await repo.find_match_by_id(fixture_id)

    if not match:
        await callback.answer("Матч не знайдено 😔", show_alert=True)
        return

    # Завантажуємо деталі, якщо їх ще немає (lineups завжди, events+stats для завершених)
    details_service = Container.get().match_details
    match = await details_service.ensure_details(match)

    # Рендеримо базові деталі матчу
    text = render_match_details(match)
    kb = get_match_details_kb(match) #Події, Статистика, Склади, Назад

    await callback.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
    await callback.answer()


# Якщо в тебе є вибір дати (вчора/завтра) — приклад хендлерів
@router.callback_query(F.data == "matches_yesterday")
async def show_yesterday_matches(callback: CallbackQuery):
    # аналогічно show_today_matches, але з day = date.today() - timedelta(days=1)
    pass

@router.callback_query(F.data == "matches_tomorrow")
async def show_tomorrow_matches(callback: CallbackQuery):
    pass


# Якщо потрібен back до списку матчів з деталів — можна в navigation_router, або тут
@router.callback_query(F.data == "back_to_matches")
async def back_to_matches(callback: CallbackQuery):
    await show_today_matches(callback.message)
    await callback.answer()