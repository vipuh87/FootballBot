from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


DATES_PER_PAGE = 8
CHAMPION_TEAMS_PER_PAGE = 12


def predictions_menu_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="✅ Узяти участь", callback_data="pred:join")
    builder.button(text="🏟 Турнір", callback_data="pred:tournament")
    builder.button(text="📅 Матчі", callback_data="pred:matches")
    builder.button(text="📝 Мої прогнози", callback_data="pred:mine")
    builder.button(text="🏆 Таблиця", callback_data="pred:standings")
    builder.button(text="📜 Правила", callback_data="pred:rules")
    builder.button(text="⬅️ Назад", callback_data="main_menu")
    builder.adjust(1, 2, 2, 2, 1)
    return builder.as_markup()


def predictions_back_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="⬅️ До прогнозів", callback_data="pred:menu")
    return builder.as_markup()


def champion_teams_kb(teams: list[dict], page: int = 0) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    total_pages = max(1, (len(teams) + CHAMPION_TEAMS_PER_PAGE - 1) // CHAMPION_TEAMS_PER_PAGE)
    page = max(0, min(page, total_pages - 1))
    start = page * CHAMPION_TEAMS_PER_PAGE
    for team in teams[start:start + CHAMPION_TEAMS_PER_PAGE]:
        team_id = team.get("api_football_team_id")
        if team_id is None:
            continue
        builder.button(text=team.get("name_uk") or team.get("name"), callback_data=f"pred:champ_pick:{team_id}")

    if page > 0:
        builder.button(text="⬅️ Попередні", callback_data=f"pred:champ_page:{page - 1}")
    if page < total_pages - 1:
        builder.button(text="Наступні ➡️", callback_data=f"pred:champ_page:{page + 1}")
    builder.button(text="⬅️ До прогнозів", callback_data="pred:menu")
    builder.adjust(2, 2, 2, 2, 2, 2, 2)
    return builder.as_markup()


def prediction_reminder_kb(fixture_id: int | None = None) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    if fixture_id is not None:
        builder.button(text="Зробити прогноз", callback_data=f"pred:match:{fixture_id}")
    builder.button(text="Меню прогнозів", callback_data="pred:menu")
    builder.adjust(1)
    return builder.as_markup()


def matches_menu_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="⏭ Найближчі матчі", callback_data="pred:upcoming")
    builder.button(text="📆 Матчі по датах", callback_data="pred:dates:0")
    builder.button(text="⬅️ До прогнозів", callback_data="pred:menu")
    builder.adjust(1)
    return builder.as_markup()


def dates_kb(dates: list[str], page: int = 0) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    total_pages = max(1, (len(dates) + DATES_PER_PAGE - 1) // DATES_PER_PAGE)
    page = max(0, min(page, total_pages - 1))
    start = page * DATES_PER_PAGE
    for day in dates[start:start + DATES_PER_PAGE]:
        builder.button(text=day, callback_data=f"pred:date:{day}")

    if page > 0:
        builder.button(text="⬅️ Попередні", callback_data=f"pred:dates:{page - 1}")
    if page < total_pages - 1:
        builder.button(text="Наступні ➡️", callback_data=f"pred:dates:{page + 1}")
    builder.button(text="⬅️ До матчів", callback_data="pred:matches")
    builder.adjust(2, 2, 2, 2, 2)
    return builder.as_markup()


def matches_kb(matches: list[dict], back_callback: str = "pred:matches") -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for match in matches:
        builder.button(
            text=f"{match.get('home_uk') or match['home']} - {match.get('away_uk') or match['away']}",
            callback_data=f"pred:match:{match['fixture_id']}",
        )
    builder.button(text="⬅️ Назад", callback_data=back_callback)
    builder.adjust(1)
    return builder.as_markup()


def match_prediction_kb(fixture_id: int, locked: bool) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    if not locked:
        common_scores = [
            (0, 0), (1, 0), (0, 1),
            (1, 1), (2, 0), (0, 2),
            (2, 1), (1, 2), (2, 2),
            (3, 0), (0, 3), (3, 1),
            (1, 3), (3, 2), (2, 3),
        ]
        for home_score, away_score in common_scores:
            builder.button(
                text=f"{home_score}:{away_score}",
                callback_data=f"pred:score:{fixture_id}:{home_score}:{away_score}",
            )
        builder.button(text="✍️ Інший рахунок", callback_data=f"pred:manual:{fixture_id}")

    builder.button(text="⬅️ До матчів", callback_data="pred:matches")
    builder.adjust(3, 3, 3, 3, 3, 1, 1)
    return builder.as_markup()
