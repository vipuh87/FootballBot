from application.services.team_service import highlight_team
from presentation.views.formatters import format_match_header, format_match_score
from presentation.views.keyboards import match_detail_keyboard
from data.icons import ICONS
import re
from typing import Optional, Tuple


def parse_round(round_str: Optional[str]) -> Tuple[Optional[int], Optional[str]]:
    if not round_str:
        return None, None

    match = re.search(r"\d+", round_str)
    if match:
        return int(match.group()), None

    return None, round_str

def render_match_details(match):
    home = highlight_team(match.home)
    away = highlight_team(match.away)
    league = (match.league)
    season = league.get("season")
    round_number, round_stage = parse_round(league.get("round", ""))
    header = format_match_header(league.get("name"), league.get("country"))
    score = format_match_score(match)

    round_text = (
        f"Тур {round_number}"
        if round_number is not None
        else round_stage
    )

    text = (
        f"{header}"
        f"{ICONS.get('vs')} {home} — {away}\n"
        f"{score}\n\n"
        f"{ICONS.get('info')} Сезон - {season}, {round_text}\n"
        f"{ICONS.get('stadium')} Стадіон - {match.venue}\n"
    )

    if match.referee:
        text += f"{ICONS.get('ref')} Суддя - {match.referee}\n"

    return text, match_detail_keyboard(match.fixture_id)
