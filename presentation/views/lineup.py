# presentation/views/lineup.py
from presentation.views.keyboards import lineup_team_choice_keyboard, single_back_keyboard
from data.icons import ICONS


def render_lineup_menu(fid: int, team1: str, team2: str):
    return "👥 <b>Оберіть склад команди:</b>", lineup_team_choice_keyboard(fid, team1, team2)


def render_lineup(team_name: str, coach: str, start_xi: list, subs: list) -> tuple:
    text = (
        f"{ICONS['lineup']} <b>{team_name}</b>\n\n"
        f"{ICONS['coach']} <b>Тренер:</b> {coach}\n\n"
        f"{ICONS['startX']} <b>Стартовий склад:</b>\n"
    )

    for i, p in enumerate(start_xi or [], 1):
        player = p.get("player")
        name = player.get("name", "?")
        number = player.get("number", "")
        text += f"{i}. {name} {number}\n"

    text += f"\n{ICONS['sub']} <b>Заміни:</b>\n"

    for i, p in enumerate(subs or [], 1):
        player = p.get("player")
        name = player.get("name", "?")
        number = player.get("number", "")
        text += f"{i}. {name} {number}\n"

    return text, single_back_keyboard()