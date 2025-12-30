# presentation/views/lineup.py
from aiogram.types import InlineKeyboardMarkup
from presentation.keyboards.main_menu import get_single_back_keyboard
from presentation.keyboards.match_details import get_lineups_kb
from data.icons import ICONS


def render_lineup_menu(fid: int, team1: str, team2: str):
    return "👥 <b>Оберіть склад команди:</b>", get_lineups_kb(fid, team1, team2)


# presentation/views/lineup.py (змінюємо render_lineup)

def render_lineup(lineup_data: dict, fixture_id) -> tuple[str, InlineKeyboardMarkup]:
    name = lineup_data["team"]["name"]
    coach = lineup_data["coach"]["name"]
    start_xi = lineup_data.get("startXI", [])
    subs = lineup_data.get("substitutes", [])

    text = (
        f"{ICONS['lineup']} <b>{name}</b>\n\n"
        f"{ICONS['coach']} <b>Тренер:</b> {coach}\n\n"
        f"{ICONS['startX']} <b>Стартовий склад:</b>\n"
    )

    for i, p in enumerate(start_xi, 1):
        player = p.get("player", {})
        name = player.get("name", "?")
        number = player.get("number", "")
        text += f"{i}. {name} {number}\n"

    text += f"\n{ICONS['sub']} <b>Заміни:</b>\n"
    for i, p in enumerate(subs, 1):
        player = p.get("player", {})
        name = player.get("name", "?")
        number = player.get("number", "")
        text += f"{i}. {name} {number}\n"

    kb = get_single_back_keyboard(f"lineups:{fixture_id}")

    return text, kb