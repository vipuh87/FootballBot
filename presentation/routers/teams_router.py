from aiogram import Router, F
from aiogram.types import CallbackQuery, Message

from application.container import Container
from application.services.team_service import get_all_teams, highlight_team  # або інші функції

# View для рендеру списку команд
from presentation.views.teams import render_teams  # підправ назву, якщо інакше (наприклад, render_teams)

# Keyboard для команд
from presentation.keyboards.main_menu import get_main_menu_kb  # або окрема для команд, якщо є
# Якщо є inline-кнопки на конкретну команду — імпортуй свою клавіатуру

router = Router(name="teams_router")


# Вхід у розділ "Команди" з головного меню (callback з кнопки)
@router.callback_query(F.data == "teams")  # підправ data під кнопку в main_menu_keyboard (наприклад, "show_teams")
async def show_teams_list(callback: CallbackQuery):
    teams = get_all_teams()  # повертає dict {team_id: team_data}

    if not teams:
        await callback.message.edit_text("Відстежувані команди не налаштовані.")
        await callback.answer()
        return

    text = render_teams(teams)  # твоя view-функція для списку команд (з іконками, назвами тощо)

    # Клавіатура: back до головного меню + можливо inline на кожну команду
    kb = get_main_menu_kb()  # або спеціальна з кнопками "Команда X" → callback "team_123"

    await callback.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
    await callback.answer()


# Опціонально: деталі конкретної команди (якщо є кнопка на команду)
@router.callback_query(F.data.startswith("team_"))
async def show_team_detail(callback: CallbackQuery):
    team_id = int(callback.data.split("_")[1])

    team_data = Container.get().team_service.get_team(team_id)  # або з data.selected_teams
    if not team_data:
        await callback.answer("Команда не знайдена", show_alert=True)
        return

    # Рендер деталів команди (наприклад, список українських гравців у клубі)
    #from presentation.views.teams import render_team_detail  # якщо є окрема функція
    #text = render_team_detail(team_data)

    kb = get_main_menu_kb()  # або з back до списку команд

   # await callback.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
   # await callback.answer()


# Опціонально: команда /teams для прямого доступу
# @router.message(Command("teams"))
# async def cmd_teams(message: Message):
#     await show_teams_list_from_message(message)
#
# async def show_teams_list_from_message(message: Message):
#     # аналогічно show_teams_list, але message.answer замість edit_text