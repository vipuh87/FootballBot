# presentation/routers/players_router.py

from aiogram import Router, F
from aiogram.types import CallbackQuery

from application.container import Container

# View для рендеру виступу українських гравців
# Зазвичай приймає match: Match → str (з використанням UkrainianPlayerPerformanceService всередині view або тут)
from presentation.views.players import render_players  # або render_players_performance, підправ назву

# Keyboard з back до деталей матчу
from presentation.keyboards.match_details import get_match_details_kb

router = Router(name="players_router")


# Вхід у розділ українських гравців для конкретного матчу
# Префікс callback_data — підправ під свій (наприклад, "ukr_players_", "players_")
@router.callback_query(F.data.startswith("ukr_players_"))
async def show_ukrainian_players(callback: CallbackQuery):
    fixture_id = int(callback.data.split("_")[2])  # підправ індекс, якщо префікс довший (наприклад, split("_")[1] якщо "ukr_players_12345")

    repo = Container.get().repo
    match = await repo.find_match_by_id(fixture_id)

    if not match:
        await callback.answer("Матч не знайдено", show_alert=True)
        return

    # Якщо view сама обробляє performance — просто передаємо match
    text = render_players(match)  # ← правильний формат: view приймає match і рендерить

    # Якщо view потребує попереднього розрахунку:
    # player_perf_service = Container.get().player_performance  # UkrainianPlayerPerformanceService
    # ua_info = []  # логіка збору, або з players_service
    # text = render_ukrainian_players(match, ua_info)

    if "немає відстежуваних гравців" in text.lower() or not text.strip():
        await callback.answer("Немає даних про українських гравців у цьому матчі", show_alert=True)
        return

    kb = get_match_details_kb(match.fixture_id)  # back + інші кнопки деталей

    await callback.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
    await callback.answer()


# Якщо є окремий вхід у розділ "Українські гравці" без матчу (наприклад, загальний список)
# @router.callback_query(F.data == "ukrainian_players_general")
# async def general_ukrainian_players(callback: CallbackQuery):
#     # Логіка для загального огляду (з news_digest або окремо)
#     pass