# presentation/views/teams_router.py
from presentation.keyboards.main_menu import get_single_back_keyboard


def render_teams(teams):
    if not teams:
        return "⚠️ Немає клубів", get_single_back_keyboard("back_to_digest")

    text = "🏟 <b>Команди, які відстежуються:</b>\n\n"

    for team in teams:
        text += f"• {team[1].get('name')}\n"

    return text, get_single_back_keyboard("main_menu")