# presentation/views/push.py
from datetime import datetime

from application.services.team_service import highlight_team
from presentation.views.formatters import (
    format_match_time,
    random_match_is_soon_phrase,
    random_no_players_phrase
)
from config import TZ_UKRAINE, TZ_ITALY
from data.icons import ICONS


def render_reminder_text(match, ua_info):
    when = format_match_time(match)
    home = highlight_team(match.home)
    away = highlight_team(match.away)

    text = (
        f"{ICONS['megaphone']} <b>{random_match_is_soon_phrase()}</b>\n\n"
        f"{home} {ICONS['vs']} {away}\n"
        f"{ICONS['rocket']} Початок: {when}\n\n"
    )

    if not ua_info:
        # Для українських клубів — просто базовий текст без блоку гравців
        return text + "Удачі в матчі! ⚽"

    lines = ["<b>Українські гравці:</b>"]

    has_any_in_squad = False  # Для перевірки, чи є хоч один у заявці

    for info in ua_info:
        player = info["name"]
        team_name = info["team"]
        start = info.get("start")
        subs = info.get("sub")

        if start or subs:
            has_any_in_squad = True

        # Назва команди (один раз на команду)
        if lines[-1] != f"\n🏟 <b>{team_name}</b>:":
            lines.append(f"\n🏟 <b>{team_name}</b>:")

        # Старт
        if start:
            if len(start) == 1:
                names = start[0]["name"]
            else:
                names = ", ".join(p["name"] for p in start)
            lines.append(f"✅ <b>У стартовому складі є:</b> {names}")

        # Лавка
        if subs:
            if len(subs) == 1:
                names = subs[0]["name"]
            else:
                names = ", ".join(p["name"] for p in subs)
            lines.append(f"🪑 <b>На лавці:</b> {names}")

    # Якщо всі українці не в заявці — дотепна фраза
    if not has_any_in_squad and ua_info:
        team_name = ua_info[0]["team"]  # Беремо першу команду
        lines.append("")
        lines.append(random_no_players_phrase(team_name))

    text += "\n\n".join(lines) + "\n\nУдачі в матчі! ⚽"

    return text


def render_last_update_text(last_update: datetime | None):

    if not last_update:
        return ""

    ua = last_update.astimezone(TZ_UKRAINE).strftime("%d.%m %H:%M")
    it = last_update.astimezone(TZ_ITALY).strftime("%H:%M")

    return f"\n\n\n<blockquote><i>Оновлено: {ua} {ICONS['ua_flag']} / {it} {ICONS['it_flag']}</i></blockquote>"
