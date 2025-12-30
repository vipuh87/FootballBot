# application/services/match_factory.py
from typing import Dict, List, Any
from domain.models.match import Match
from application.services.team_service import is_selected_team  # ← додано імпорт


def _extract_list_field(item: Dict[str, Any], key: str) -> List:
    val = item.get(key)

    if val is None:
        return []

    if isinstance(val, list):
        return val

    if isinstance(val, dict):
        resp = val.get("response")
        if isinstance(resp, list):
            return resp
        inner = val.get(key)
        if isinstance(inner, list):
            return inner
        return []

    return []


def matches_from_api_day(data: Dict) -> List[Match]:
    """Створює список Match з raw даних дня, фільтруючи по SELECTED_TEAM_IDS"""
    resp = data.get("response") if isinstance(data, dict) else []
    matches: List[Match] = []

    for item in resp:
        try:
            # Витягуємо ID команд для фільтрації
            home_id = (item.get("teams", {}).get("home") or {}).get("id")
            away_id = (item.get("teams", {}).get("away") or {}).get("id")

            # Фільтрація: тільки матчі з SELECTED_TEAM_IDS
            if not (is_selected_team(home_id) or is_selected_team(away_id)):
                continue  # пропускаємо нецікавий матч

            # Створюємо Match
            match = Match.from_api_fixture(item)

            # Додаємо деталі, якщо є в raw
            statistics_list = _extract_list_field(item, "statistics")
            events_list = _extract_list_field(item, "events")
            lineups_list = _extract_list_field(item, "lineups")

            if statistics_list:
                match.statistics = statistics_list
            if events_list:
                match.events = events_list
            if lineups_list:
                match.lineups = lineups_list

            matches.append(match)

        except Exception as e:
            try:
                fid = (item.get("fixture") or {}).get("id")
            except Exception:
                fid = None
            print(f"❌ MATCH FACTORY ERROR (fixture={fid}):", repr(e))
            continue

    return matches