# presentation/views/players.py
from presentation.views.keyboards import single_back_keyboard


def html_escape(text: str) -> str:
    if not text:
        return ""
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def render_players(teams: list):
    text = "<b>🇺🇦 Гравці, які відслідковуються:</b>\n\n"
    found = False

    for team in teams:
        if team[1].get("is_ukrainian"):
            continue

        players = team[1].get("players")
        if not players:
            continue

        found = True
        team_name = html_escape(team[1].get("name"))

        for p in players:
            name = html_escape(players.get(p))
            text += f"• <b>{name}</b> ({team_name})\n"

        text += "\n"

    if not found:
        text += "⚠️ Немає гравців для відображення"

    return text, single_back_keyboard("back_to_digest")