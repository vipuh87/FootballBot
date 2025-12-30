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
        f"{render_ukrainian_players_block(ua_info)}\n"
        f"Матч почнеться менше ніж через 15 хв."
    )
    return text

def render_ukrainian_players_block(ua_info: list) -> str:
    if not ua_info:
        return ""

    lines = [f"{ICONS['ua_flag']} <b>Українці у матчі:</b>"]

    for team in ua_info:
        team_name = team.get("team_name", "—")
        start = team.get("start", [])
        subs = team.get("subs", [])

        # ✅ Якщо взагалі нікого немає
        if not start and not subs:
            lines.append(random_no_players_phrase(team_name))
            continue

        # ✅ Назва команди
        lines.append(f"\n🏟 <b>{team_name}</b>:")

        # ✅ Старт
        if start:
            if len(start) == 1:
                names = start[0]["name"]
            else:
                names = ", ".join(p["name"] for p in start)

            lines.append(f"✅ <b>У стартовому складі є:</b> {names}")

        # ✅ Лавка
        if subs:
            if len(subs) == 1:
                names = subs[0]["name"]
            else:
                names = ", ".join(p["name"] for p in subs)

            lines.append(f"🪑 <b>На лавці:</b> {names}")

    return "\n\n".join(lines)

def render_last_update_text(last_update: datetime | None):

    if not last_update:
        return ""

    ua = last_update.astimezone(TZ_UKRAINE).strftime("%d.%m %H:%M")
    it = last_update.astimezone(TZ_ITALY).strftime("%H:%M")

    return f"\n\n\n<blockquote><i>Оновлено: {ua} {ICONS['ua_flag']} / {it} {ICONS['it_flag']}</i></blockquote>"
