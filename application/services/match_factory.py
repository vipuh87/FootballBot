from typing import Dict, List, Any
from domain.models.match import Match


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
    resp = data.get("response") if isinstance(data, dict) else []
    matches: List[Match] = []

    for item in resp:
        try:
            match = Match.from_api_fixture(item)

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
