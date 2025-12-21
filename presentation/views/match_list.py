# presentation/views/match_list.py
from application.services.team_service import highlight_team
from application.container import Container
from presentation.views.formatters import format_match_score, format_match_header, random_no_match_phrase
from presentation.keyboards.matches import get_day_kb, get_match_card_kb
from datetime import date
from data.icons import ICONS
from aiogram.utils.keyboard import InlineKeyboardBuilder
from presentation.views.push import render_last_update_text


async def render_matches_list(matches: list, day: date, current_day_offset: int = 0):
    repo = Container.get().repo

    if not matches:
        from presentation.views.digest_view import render_main_digest
        text, kb = await render_main_digest()
        return text, kb

    lines = []
    builder = InlineKeyboardBuilder()

    # Кнопки для кожного матчу
    for match in matches:
        home = highlight_team(match.home)
        away = highlight_team(match.away)

        lines.append(
            f"{format_match_header(match.league.get('name'), match.league.get('country'))}"
            f"{ICONS.get('vs')} {home} — {away}\n"
            f"{format_match_score(match)}"
        )
        builder.row(*get_match_card_kb(match))  # кнопка detail:

    header = f"{ICONS['calendar']} Матчі на {day.strftime('%d.%m.%Y')}\n\n"
    text = header + "\n\n".join(lines)

    last_update = await repo.get_last_update(day)
    text += render_last_update_text(last_update)

    day_kb = get_day_kb(day, current_day_offset=current_day_offset)
    for row in day_kb.inline_keyboard:
        builder.row(*row)

    return text, builder.as_markup()