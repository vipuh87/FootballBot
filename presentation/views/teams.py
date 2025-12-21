# presentation/views/teams.py
from presentation.views.keyboards import single_back_keyboard


def render_teams(teams):
    if not teams:
        return "⚠️ Немає клубів", single_back_keyboard("back_to_digest")

    text = "🏟 <b>Команди, які відстежуються:</b>\n\n"

    for team in teams:
        text += f"• {team[1].get('name')}\n"

    return text, single_back_keyboard("back_to_digest")