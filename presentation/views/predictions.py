from __future__ import annotations

from datetime import datetime
from html import escape
from data.icons import ICONS

from config import TZ_ITALY, TZ_UKRAINE


def _format_dual_dt(date_utc: str | datetime) -> str:
    dt = date_utc if isinstance(date_utc, datetime) else datetime.fromisoformat(date_utc.replace("Z", "+00:00"))
    italy = dt.astimezone(TZ_ITALY).strftime("%d.%m.%Y %H:%M")
    ukraine = dt.astimezone(TZ_UKRAINE).strftime("%H:%M")
    return f"{italy} {ICONS['it_flag']} / {ukraine} {ICONS['ua_flag']}"


def render_prediction_menu(participant: dict | None, champion: dict | None = None) -> str:
    if participant:
        name = escape(participant["display_name"])
        status = f"Ти вже береш участь як <b>{name}</b>."
    else:
        status = "Натисни «Узяти участь», щоб потрапити в спільну таблицю."

    champion_text = (
        f"Твій чемпіон: <b>{escape(champion['champion'])}</b>."
        if champion
        else "Прогноз чемпіона ще не зроблено."
    )

    return (
        "<b>🏆 Прогнози ЧС-2026</b>\n\n"
        f"{status}\n"
        f"{champion_text}\n\n"
        "Турнір спільний для всіх учасників з усіх груп, де працює бот."
    )


def render_champion(champion: dict | None, service) -> str:
    lock_time = service.champion_lock_time()
    if lock_time:
        lock_text = f"Змінювати прогноз можна до {_format_dual_dt(lock_time)}."
    else:
        lock_text = "Дедлайн стане доступним після додавання розкладу."

    current = f"Твій прогноз: <b>{escape(champion['champion'])}</b>\n\n" if champion else "Ти ще не обрав чемпіона.\n\n"
    if service.is_champion_locked():
        lock_text = "Прогноз чемпіона вже закрито."

    return (
        "<b>🏅 Прогноз чемпіона ЧС-2026</b>\n\n"
        f"{current}"
        f"{lock_text}\n\n"
        "Обери збірну кнопкою нижче або напиши її назву повідомленням."
    )


def render_matches_menu(total_matches: int, total_dates: int) -> str:
    return (
        "<b>📅 Матчі ЧС-2026</b>\n\n"
        f"У розкладі: <b>{total_matches}</b> матчів, <b>{total_dates}</b> ігрових днів.\n"
        "Щоб список не перетворився на стіну тексту, матчі розбиті на найближчі і перегляд по датах."
    )


def render_dates_page(dates: list[str], page: int, per_page: int) -> str:
    if not dates:
        return "<b>📆 Матчі по датах</b>\n\nРозклад ще не додано."

    total_pages = max(1, (len(dates) + per_page - 1) // per_page)
    page = max(0, min(page, total_pages - 1))
    return (
        "<b>📆 Матчі по датах</b>\n\n"
        f"Сторінка {page + 1}/{total_pages}. Обери дату, щоб побачити матчі цього дня."
    )


def render_matches(matches: list[dict], service, user_id: int | None = None, title: str = "📅 Матчі ЧС-2026") -> str:
    if not matches:
        return f"<b>{escape(title)}</b>\n\nМатчів у цьому розділі поки немає."

    lines = [f"<b>{escape(title)}</b>\n"]
    for match in matches:
        locked = service.is_locked(match)
        prediction = service.user_prediction(user_id, match["fixture_id"]) if user_id else None
        prediction_text = f" | твій прогноз: <b>{prediction['home_score']}:{prediction['away_score']}</b>" if prediction else ""
        lock_text = "🔒 закрито" if locked else f"дедлайн {_format_dual_dt(service.lock_time(match))}"
        result = ""
        if match.get("score_home") is not None and match.get("score_away") is not None:
            result = f" | результат: <b>{match['score_home']}:{match['score_away']}</b>"
        lines.append(
            f"• <b>{escape(match.get('home_uk') or match['home'])} - {escape(match.get('away_uk') or match['away'])}</b>\n"
            f"  {escape(match.get('stage', ''))} | старт {_format_dual_dt(match['date_utc'])}\n"
            f"  {lock_text}{prediction_text}{result}"
        )
    return "\n\n".join(lines)


def render_match(match: dict, service, prediction: dict | None) -> str:
    locked = service.is_locked(match)
    if not service.is_match_resolved(match):
        lock_text = "Команди цього матчу ще не визначені. Прогноз відкриється після оновлення фікстури."
    else:
        lock_text = "Прийом прогнозів закрито." if locked else f"Прогноз можна змінювати до {_format_dual_dt(service.lock_time(match))}."
    prediction_text = (
        f"Твій прогноз: <b>{prediction['home_score']}:{prediction['away_score']}</b>\n"
        if prediction
        else "Ти ще не зробив прогноз на цей матч.\n"
    )
    result_text = ""
    if match.get("score_home") is not None and match.get("score_away") is not None:
        result_text = f"\nРезультат за 90 хвилин: <b>{match['score_home']}:{match['score_away']}</b>\n"

    return (
        f"<b>{escape(match.get('home_uk') or match['home'])} - {escape(match.get('away_uk') or match['away'])}</b>\n"
        f"{escape(match.get('stage', ''))}\n"
        f"Початок: {_format_dual_dt(match['date_utc'])}\n\n"
        f"{prediction_text}"
        f"{lock_text}"
        f"{result_text}"
    )


def _is_group_stage(match: dict) -> bool:
    value = " ".join(str(match.get(key, "")) for key in ("stage", "round", "group")).casefold()
    return "group" in value or "груп" in value


def _group_name(match: dict) -> str:
    group = match.get("group")
    if group:
        return str(group)
    stage = str(match.get("stage") or "Груповий етап")
    return stage


def _team_row() -> dict:
    return {"played": 0, "points": 0, "wins": 0, "draws": 0, "losses": 0, "gf": 0, "ga": 0}


def render_tournament_structure(matches: list[dict]) -> str:
    if not matches:
        return "<b>🏟 Турнір ЧС-2026</b>\n\nРозклад ще не додано."

    groups: dict[str, dict[str, dict]] = {}
    knockout: dict[str, list[dict]] = {}
    for match in matches:
        if _is_group_stage(match):
            group = groups.setdefault(_group_name(match), {})
            home = match.get("home_uk") or match.get("home") or "TBD"
            away = match.get("away_uk") or match.get("away") or "TBD"
            group.setdefault(home, _team_row())
            group.setdefault(away, _team_row())
            if match.get("score_home") is None or match.get("score_away") is None:
                continue

            home_score = int(match["score_home"])
            away_score = int(match["score_away"])
            home_row = group[home]
            away_row = group[away]
            home_row["played"] += 1
            away_row["played"] += 1
            home_row["gf"] += home_score
            home_row["ga"] += away_score
            away_row["gf"] += away_score
            away_row["ga"] += home_score
            if home_score > away_score:
                home_row["wins"] += 1
                away_row["losses"] += 1
                home_row["points"] += 3
            elif home_score < away_score:
                away_row["wins"] += 1
                home_row["losses"] += 1
                away_row["points"] += 3
            else:
                home_row["draws"] += 1
                away_row["draws"] += 1
                home_row["points"] += 1
                away_row["points"] += 1
        else:
            knockout.setdefault(str(match.get("stage") or "Плейоф"), []).append(match)

    lines = ["<b>🏟 Турнір ЧС-2026</b>"]
    if groups:
        for group_name, teams in sorted(groups.items()):
            lines.extend(["", f"<b>{escape(group_name)}</b>", "<pre>Збірна           О  М  РМ"])
            ordered = sorted(
                teams.items(),
                key=lambda item: (
                    -item[1]["points"],
                    -(item[1]["gf"] - item[1]["ga"]),
                    -item[1]["gf"],
                    item[0].casefold(),
                ),
            )
            for team, row in ordered:
                diff = row["gf"] - row["ga"]
                diff_text = f"+{diff}" if diff > 0 else str(diff)
                line = f"{_short_name(team):<16}{row['points']:>2}{row['played']:>3}{diff_text:>4}"
                lines.append(escape(line))
            lines.append("</pre>")

    if knockout:
        lines.extend(["", "<b>Плейоф</b>"])
        for stage, stage_matches in sorted(knockout.items()):
            lines.append(f"\n<b>{escape(stage)}</b>")
            for match in sorted(stage_matches, key=lambda item: item.get("date_utc") or "")[:12]:
                result = ""
                if match.get("score_home") is not None and match.get("score_away") is not None:
                    result = f" {match['score_home']}:{match['score_away']}"
                lines.append(
                    f"• {escape(match.get('home_uk') or match.get('home', 'TBD'))} - {escape(match.get('away_uk') or match.get('away', 'TBD'))}"
                    f"{escape(result)} | {_format_dual_dt(match['date_utc'])}"
                )

    if not groups and not knockout:
        lines.append("\nСтадії турніру з'являться після додавання розкладу.")
    else:
        lines.append("\nО - очки, М - зіграні матчі, РМ - різниця м'ячів.")
    return "\n".join(lines)


def render_my_predictions(matches: list[dict], predictions: dict, champion: dict | None) -> str:
    lines = ["<b>📝 Мої прогнози</b>\n"]
    if champion:
        lines.append(f"🏅 Чемпіон: <b>{escape(champion['champion'])}</b>\n")
    else:
        lines.append("🏅 Чемпіон: ще не обрано\n")

    if not predictions:
        lines.append("Прогнозів на матчі поки немає.")
        return "\n".join(lines)

    matches_by_id = {str(m["fixture_id"]): m for m in matches}
    for fixture_id, prediction in sorted(predictions.items()):
        match = matches_by_id.get(fixture_id)
        if not match:
            continue
        lines.append(
            f"• {escape(match.get('home_uk') or match['home'])} - {escape(match.get('away_uk') or match['away'])}: "
            f"<b>{prediction['home_score']}:{prediction['away_score']}</b>"
        )
    return "\n".join(lines)


def _short_name(name: str, width: int = 12) -> str:
    clean = " ".join(name.split())
    return clean if len(clean) <= width else clean[: width - 1] + "…"


def render_standings(rows: list[dict], current_user_id: int | None = None) -> str:
    if not rows:
        return "<b>🏆 Таблиця прогнозів</b>\n\nУчасників поки немає."

    lines = [
        "<b>🏆 Таблиця прогнозів ЧС-2026</b>",
        "",
        "<pre>#Учасник    О  М  10 7  5  3  0",
    ]

    current_rank = 0
    last_points = None
    for index, row in enumerate(rows, 1):
        if row["points"] != last_points:
            current_rank = index
            last_points = row["points"]

        champion_col = str(row["champion_points"] // 10) if row.get("champion_resolved") else "0"
        line = (
            f"{str(current_rank) + '.':<2}"
            f"{_short_name(row['display_name']):<9}"
            f"{row['points']:>3}"
            f"|{row['played']:>2}"
            f"|{champion_col:>2}"
            f"|{row['rare']:>2}"
            f"|{row['exact'] - row['rare']:>2}"
            f"|{row['correct'] - row['exact']:>2}"
            f"|{row['zero']:>2}"
        )
        escaped_line = escape(line)
        if current_user_id is not None and int(row["user_id"]) == int(current_user_id):
            escaped_line = f"<b>{escaped_line}</b>"
        lines.append(escaped_line)

    lines.append("</pre>")
    lines.append(
        "О - очки, "
        "М - зіграні матчі з прогнозом, "
        "10 - вгаданий чемпіон, "
        "7 - рідкісний точний рахунок, "
        "5 - точний рахунок, "
        "3 - вгаданий результат, "
        "0 - матчі без очок."
    )
    return "\n".join(lines)
