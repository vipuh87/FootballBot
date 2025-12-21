# models/match.py
from __future__ import annotations
from dataclasses import dataclass, asdict, field
from typing import Optional, List, Dict, Any


@dataclass
class Match:
    fixture_id: int
    league: Optional[Dict[str, Any]]
    venue: str
    referee: Optional[str]
    home_id: Optional[int]
    home: str
    away_id: Optional[int]
    away: str
    date_utc: Optional[str]
    status: str

    score_home: Optional[int] = None
    score_away: Optional[int] = None

    events: Optional[List[Dict[str, Any]]] = field(default=None)
    statistics: Optional[List[Dict[str, Any]]] = field(default=None)
    lineups: Optional[List[Dict[str, Any]]] = field(default=None)

    _raw_fixture: Optional[Dict[str, Any]] = field(default=None, repr=False)

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d.pop("_raw_fixture", None)
        return d

    @staticmethod
    def from_api_fixture(fixture_wrapper: Dict[str, Any]) -> "Match":
        fixture = fixture_wrapper.get("fixture", {})
        league = fixture_wrapper.get("league", {})
        teams = fixture_wrapper.get("teams", {})
        goals = fixture_wrapper.get("goals", {}) or {}

        venue_obj = fixture.get("venue") or {}
        venue = venue_obj.get("name")
        city = venue_obj.get("city")
        full_venue = f"{venue}, {city}" if venue and city else venue

        referee = fixture.get("referee")

        return Match(
            fixture_id=fixture.get("id"),
            league=league,
            venue=full_venue,
            referee=referee,
            home_id=(teams.get("home") or {}).get("id"),
            home=(teams.get("home") or {}).get("name", "Home"),
            away_id=(teams.get("away") or {}).get("id"),
            away=(teams.get("away") or {}).get("name", "Away"),
            date_utc=fixture.get("date"),
            status=(fixture.get("status") or {}).get("short", "—"),
            score_home=goals.get("home"),
            score_away=goals.get("away"),
            events=None,
            statistics=None,
            lineups=None,
            _raw_fixture=fixture_wrapper
        )

    def to_api_fixture_wrapper(self) -> Dict[str, Any]:
        if self._raw_fixture:
            wrapper = dict(self._raw_fixture)  # shallow copy
        else:
            wrapper = {
                "fixture": {
                    "id": self.fixture_id,
                    "date": self.date_utc,
                    "status": {"short": self.status},
                },
                "league": self.league if isinstance(self.league, dict) else {"name": self.league},
                "teams": {
                    "home": {"id": self.home_id, "name": self.home},
                    "away": {"id": self.away_id, "name": self.away},
                },
                "goals": {"home": self.score_home, "away": self.score_away},
            }

        if self.events is not None:
            wrapper["events"] = {
                "get": "fixtures/events",
                "parameters": {"fixture": str(self.fixture_id)},
                "errors": [],
                "results": len(self.events),
                "paging": {"current": 1, "total": 1},
                "response": self.events,
            }
        if self.statistics is not None:
            wrapper["statistics"] = {
                "get": "fixtures/statistics",
                "parameters": {"fixture": str(self.fixture_id)},
                "errors": [],
                "results": len(self.statistics) if isinstance(self.statistics, list) else 0,
                "paging": {"current": 1, "total": 1},
                "response": self.statistics,
            }
        if self.lineups is not None:
            wrapper["lineups"] = {
                "get": "fixtures/lineups",
                "parameters": {"fixture": str(self.fixture_id)},
                "errors": [],
                "results": len(self.lineups) if isinstance(self.lineups, list) else 0,
                "paging": {"current": 1, "total": 1},
                "response": self.lineups,
            }

        wrapper["goals"] = {"home": self.score_home, "away": self.score_away}

        return wrapper
