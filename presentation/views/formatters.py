import random
from datetime import datetime

from data.phrases import *
from data.icons import ICONS

from config import TZ_ITALY, TZ_UKRAINE

def random_no_match_phrase():
    return random.choice(NO_MATCH_PHRASES)

def random_match_is_soon_phrase():
    return random.choice(MATCH_IS_SOON)

def random_no_players_phrase(team_name):
    return random.choice(NO_UA_PLAYERS_TODAY_PHRASES).format(team=team_name)

def  format_match_time(match):
    try:
        dt = datetime.fromisoformat(match.date_utc.replace("Z", "+00:00"))
        it = dt.astimezone(TZ_ITALY).strftime("%H:%M")
        ua = dt.astimezone(TZ_UKRAINE).strftime("%H:%M")
        return f"{it} {ICONS['it_flag']} / {ua} {ICONS['ua_flag']}"
    except Exception:
        return "—"

def get_country_flag(country_name: str) -> str:

    if not country_name:
        return ""

    name = country_name.strip().lower()

    country_map = {
        "ukraine": "ua_flag",
        "italy": "it_flag",
        "italia": "it_flag",
        "england": "en_flag",
        "great britain": "gb_flag",
        "united kingdom": "gb_flag",
        "spain": "es_flag",
        "germany": "de_flag",
        "france": "fr_flag",
        "poland": "pl_flag",
        "brazil": "br_flag",
        "argentina": "ar_flag",
        "greece": "gr_flag",
        "portugal": "pt_flag",
    }

    icon_key = country_map.get(name)

    if not icon_key:
        return ""

    return ICONS.get(icon_key, "")

def get_league_icon(league_name: str) -> str:
    if not league_name:
        return ""

    name = league_name.lower()

    # 🏆 Кубки
    cup_keywords = [
        "cup", "coppa", "pokal", "trophy", "coupe", "copa"
    ]

    for word in cup_keywords:
        if word in name:
            return ICONS.get("cup", "")

    # ⭐ Топ ліги
    leagues_map = {
        "premier": "league",
        "serie a": "league",
        "la liga": "league",
        "bundesliga": "league",
        "ligue 1": "league",
        "eredivisie": "league",
        "primeira": "league",
    }

    for key, icon_key in leagues_map.items():
        if key in name:
            return ICONS.get(icon_key, "")

    # 🌍 Міжнародні турніри
    if "champions" in name or "ucl" in name:
        return ICONS.get("ucl", "")

    if "europa" in name or "uel" in name:
        return ICONS.get("uel", "")

    if "conference" in name:
        return ICONS.get("conference", "")

    # ⚽ Усі інші ліги
    return ICONS.get("league", "")


def format_match_header(league_name, country):
    icon = get_league_icon(league_name)
    country_flag = get_country_flag(country)

    return f"{icon} {league_name} {country_flag}\n"

def format_match_score(match):
    when = format_match_time(match)

    home_goals = match.score_home if match.score_home is not None else 0
    away_goals = match.score_away if match.score_away is not None else 0

    if match.status == "NS":
        score = f"{ICONS['time']} Почнеться о {when}"
    elif match.status in ("1H", "2H", "ET", "HT"):
        score = f"{ICONS['live']} Триває {home_goals}:{away_goals}"
    elif match.status in ("FT", "AET", "PEN"):
        score = f"{ICONS['finished']} Матч завершено {home_goals}:{away_goals}"
    else:
        score = f"{home_goals}:{away_goals}"

    return score
