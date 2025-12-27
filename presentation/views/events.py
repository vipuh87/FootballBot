# presentation/views/events.py
from presentation.keyboards.match_details import get_match_details_kb
from data.icons import ICONS


def render_events(events: list, fid: int):
    if not events:
        return f"{ICONS['warning']} Подій не знайдено", get_match_details_kb(fid)

    text = f"{ICONS['ball']} <b>Події матчу</b>\n\n"

    for e in events:
        team = e.get("team", {}).get("name", "—")
        minute = e.get("time", {}).get("elapsed", "—")
        extra = e.get("time", {}).get("extra")
        minute_str = f"{minute}'" + (f"+{extra}'" if extra else "")
        player = e.get("player", {}).get("name", "—")
        assist = e.get("assist", {}).get("name")
        detail = e.get("detail", "")
        event_type = e.get("type", "").strip().lower()

        if event_type == "goal":
            text += _render_goal_event(minute_str, team, player, assist, detail)
        elif event_type == "subst":
            text += _render_subst_event(minute_str, team, player, assist)
        elif event_type == "card":
            text += _render_card_event(minute_str, team, player, detail)
        elif event_type == "var":
            text += _render_var_event(minute_str, team, player, detail)
        else:
            text += f"{ICONS['info']} <b>{minute_str}</b> {team} — {detail} ({player})\n"

    return text, get_match_details_kb(fid)

def _render_goal_event(minute: str, team: str, player: str, assist: str | None, detail: str):
    icon = ICONS.get("goal", "⚽")
    text = f"{icon} <b>{minute}</b> {team} — Гол! {player}"
    if assist:
        text += f" (асист: {assist})"
    if "own goal" in detail.lower():
        text += " (автогол)"
    elif "penalty" in detail.lower():
        text += " (пенальті)"
    return text + "\n"


def _render_subst_event(minute: str, team: str, player_in: str, player_out: str | None):
    icon = ICONS.get("sub", "🔄")
    if player_out:
        return f"{icon} <b>{minute}</b> {team} — {player_out} ⇢ {player_in}\n"
    return f"{icon} <b>{minute}</b> {team} — {player_in}\n"


def _render_card_event(minute: str, team: str, player: str, detail: str):
    if "yellow" in detail.lower():
        icon = ICONS.get("yellow", "🟨")
    elif "red" in detail.lower():
        icon = ICONS.get("red", "🟥")
    else:
        icon = ICONS.get("card", "🟨🟥")
    return f"{icon} <b>{minute}</b> {team} — {player} ({detail})\n"


def _render_var_event(minute: str, team: str, player: str, detail: str):
    icon = ICONS.get("var", "📺")
    detail_low = detail.lower()
    if "goal cancelled" in detail_low:
        return f"{icon} <b>{minute}</b> {team} — ❌ Гол скасовано (VAR)\n"
    if "penalty confirmed" in detail_low:
        return f"{icon} <b>{minute}</b> {team} — ✅ Пенальті підтверджено (VAR)\n"
    return f"{icon} <b>{minute}</b> {team} — Перевірка VAR: {detail} ({player})\n"