from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any
from data.icons import ICONS


from config import TZ_ITALY, TZ_UKRAINE


DATA_DIR = Path("data/predictions")
TOURNAMENT_FILE = DATA_DIR / "tournament.json"
PARTICIPANTS_FILE = DATA_DIR / "participants.json"
PREDICTIONS_FILE = DATA_DIR / "predictions.json"
CHAMPION_PREDICTIONS_FILE = DATA_DIR / "champion_predictions.json"
REMINDERS_FILE = DATA_DIR / "reminders.json"
MATCHES_FILE = DATA_DIR / "world_cup_2026_matches.json"
TEAMS_FILE = DATA_DIR / "world_cup_2026_teams.json"


RULES_TEXT_UA = (
    "<b>Правила турніру прогнозів ЧС-2026</b>\n\n"
    "Гра проходить під час Чемпіонату світу з футболу 2026.\n\n"
    "<b>Прогноз чемпіона</b>\n"
    "До початку першого матчу турніру кожен учасник має обрати переможця ЧС-2026. "
    "Після стартового свистка першої гри прогноз чемпіона змінити вже не можна.\n\n"
    "<b>Прогнози на матчі</b>\n"
    "Потрібно вказати рахунок кожного матчу та підтвердити прогноз не пізніше ніж "
    "за 90 хвилин до початку гри.\n\n"
    "У розрахунок береться тільки рахунок після 90 хвилин основного часу. "
    "Додатковий час і серія пенальті не враховуються.\n\n"
    "Якщо ти вгадав результат матчу, тобто переможця або нічию, отримуєш 3 бали. "
    "Якщо також вгадав точний рахунок, отримуєш ще 2 бонусні бали.\n\n"
    "Якщо точний рахунок вгадав тільки один з учасників, які зробили прогноз "
    "на цей матч, додається ще 2 бонусні бали.\n\n"
    "Отже: правильний результат - 3 бали, точний рахунок - 5 балів, "
    "рідкісний точний рахунок - 7 балів.\n\n"
    "За правильно вгаданого переможця турніру додається 10 балів після завершення фіналу."
)


@dataclass
class ScoreResult:
    points: int
    exact: bool
    correct_outcome: bool
    rare_exact: bool


class PredictionService:
    lock_minutes_before = 90
    match_reminder_minutes_before_lock = (24 * 60, 6 * 60, 3 * 60)
    champion_reminder_minutes_before_start = (72 * 60, 24 * 60, 6 * 60)

    def __init__(self):
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        self._ensure_files()

    def _ensure_files(self) -> None:
        if not TOURNAMENT_FILE.exists():
            self._write_json(
                TOURNAMENT_FILE,
                {
                    "id": "world_cup_2026",
                    "name": "Прогнози ЧС-2026",
                    "status": "draft",
                    "lock_minutes_before": self.lock_minutes_before,
                    "champion": None,
                },
            )
        for path, default in (
            (PARTICIPANTS_FILE, {}),
            (PREDICTIONS_FILE, {}),
            (CHAMPION_PREDICTIONS_FILE, {}),
            (REMINDERS_FILE, {"sent": []}),
        ):
            if not path.exists():
                self._write_json(path, default)
        if not MATCHES_FILE.exists():
            self._write_json(MATCHES_FILE, self._default_matches())
        if not TEAMS_FILE.exists():
            self._write_json(TEAMS_FILE, [])

    def _default_matches(self) -> list[dict[str, Any]]:
        return [
            {
                "fixture_id": 2026061101,
                "date_utc": "2026-06-11T19:00:00+00:00",
                "stage": "Груповий етап",
                "home": "Mexico",
                "away": "TBD",
                "status": "NS",
                "score_home": None,
                "score_away": None,
            },
            {
                "fixture_id": 2026061201,
                "date_utc": "2026-06-12T19:00:00+00:00",
                "stage": "Груповий етап",
                "home": "TBD",
                "away": "TBD",
                "status": "NS",
                "score_home": None,
                "score_away": None,
            },
            {
                "fixture_id": 2026061301,
                "date_utc": "2026-06-13T19:00:00+00:00",
                "stage": "Груповий етап",
                "home": "TBD",
                "away": "TBD",
                "status": "NS",
                "score_home": None,
                "score_away": None,
            },
        ]

    def _read_json(self, path: Path, default: Any) -> Any:
        if not path.exists():
            return default
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            return default

    def _write_json(self, path: Path, data: Any) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp = path.with_suffix(".tmp")
        tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        tmp.replace(path)

    def _format_dual_dt(self, dt: datetime) -> str:
        italy = dt.astimezone(TZ_ITALY).strftime("%d.%m.%Y %H:%M")
        ukraine = dt.astimezone(TZ_UKRAINE).strftime("%d.%m.%Y %H:%M")
        return f"{italy} {ICONS['it_flag']} / {ukraine} {ICONS['ua_flag']}"

    def tournament(self) -> dict[str, Any]:
        return self._read_json(TOURNAMENT_FILE, {})

    def tournament_champion(self) -> dict[str, Any] | None:
        tournament = self.tournament()
        champion_team_id = tournament.get("champion_team_id")
        if champion_team_id is not None:
            team = self.find_world_cup_team_by_id(champion_team_id)
            if team:
                return team

        champion = tournament.get("champion")
        if isinstance(champion, str) and champion.strip():
            return self.find_world_cup_team_by_name(champion) or {"name_uk": champion.strip(), "name": champion.strip()}
        return None

    def matches(self) -> list[dict[str, Any]]:
        matches = self._read_json(MATCHES_FILE, [])
        return sorted(matches, key=lambda m: m.get("date_utc") or "")

    def match_dates(self) -> list[str]:
        return sorted({self.kickoff(match).date().isoformat() for match in self.matches()})

    def matches_on_utc_date(self, day) -> list[dict[str, Any]]:
        target = day.isoformat() if hasattr(day, "isoformat") else str(day)
        return [match for match in self.matches() if self.kickoff(match).date().isoformat() == target]

    def matches_by_date(self, day: str) -> list[dict[str, Any]]:
        return [match for match in self.matches() if self.kickoff(match).date().isoformat() == day]

    def upcoming_matches(self, limit: int = 8) -> list[dict[str, Any]]:
        now = datetime.now(timezone.utc)
        upcoming = [match for match in self.matches() if self.kickoff(match) >= now]
        return upcoming[:limit]

    def find_match(self, fixture_id: int) -> dict[str, Any] | None:
        return next((m for m in self.matches() if int(m["fixture_id"]) == fixture_id), None)

    def is_match_resolved(self, match: dict[str, Any]) -> bool:
        return bool(match.get("home_team_id") and match.get("away_team_id"))

    def first_match(self) -> dict[str, Any] | None:
        matches = self.matches()
        return matches[0] if matches else None

    def participants(self) -> dict[str, dict[str, Any]]:
        return self._read_json(PARTICIPANTS_FILE, {})

    def _prediction_file(self, user_id: int | str) -> Path:
        return DATA_DIR / f"predictions_{user_id}.json"

    def predictions(self) -> dict[str, dict[str, dict[str, Any]]]:
        result = {}

        files = list(DATA_DIR.glob("predictions_*.json"))

        if files:
            for file in files:
                user_id = file.stem.replace("predictions_", "")
                result[user_id] = self._read_json(file, {})

            return result

        # fallback на старий формат
        return self._read_json(PREDICTIONS_FILE, {})

    def champion_predictions(self) -> dict[str, dict[str, Any]]:
        return self._read_json(CHAMPION_PREDICTIONS_FILE, {})

    def world_cup_teams(self) -> list[dict[str, Any]]:
        teams = self._read_json(TEAMS_FILE, [])
        return teams if isinstance(teams, list) else []

    def find_world_cup_team_by_id(self, team_id: int | str | None) -> dict[str, Any] | None:
        if team_id is None:
            return None
        try:
            target_id = int(team_id)
        except (TypeError, ValueError):
            return None

        for team in self.world_cup_teams():
            try:
                current_id = int(team.get("api_football_team_id"))
            except (TypeError, ValueError):
                continue
            if current_id == target_id:
                return team
        return None

    def find_world_cup_team_by_name(self, value: str) -> dict[str, Any] | None:
        needle = " ".join(value.strip().split()).casefold()
        if not needle:
            return None

        for team in self.world_cup_teams():
            names = [
                team.get("name"),
                team.get("name_uk"),
                *(team.get("aliases") or []),
            ]
            if any(isinstance(name, str) and name.casefold() == needle for name in names):
                return team
        return None

    def register_participant(self, user, chat_id: int | None = None) -> dict[str, Any]:
        participants = self.participants()
        user_id = str(user.id)
        display_name = user.full_name or user.username or f"User {user.id}"

        participant = participants.get(user_id, {})
        source_chat_ids = set(participant.get("source_chat_ids", []))
        if chat_id is not None:
            source_chat_ids.add(chat_id)

        participant.update(
            {
                "user_id": user.id,
                "display_name": display_name,
                "username": user.username,
                "joined_at": participant.get("joined_at") or datetime.now(timezone.utc).isoformat(),
                "source_chat_ids": sorted(source_chat_ids),
            }
        )
        participants[user_id] = participant
        self._write_json(PARTICIPANTS_FILE, participants)
        return participant

    def kickoff(self, match: dict[str, Any]) -> datetime:
        return datetime.fromisoformat(match["date_utc"].replace("Z", "+00:00"))

    def lock_time(self, match: dict[str, Any]) -> datetime:
        return self.kickoff(match) - timedelta(minutes=self.lock_minutes_before)

    def is_locked(self, match: dict[str, Any]) -> bool:
        return datetime.now(timezone.utc) >= self.lock_time(match)

    def champion_lock_time(self) -> datetime | None:
        first_match = self.first_match()
        return self.kickoff(first_match) if first_match else None

    def is_champion_locked(self) -> bool:
        lock_time = self.champion_lock_time()
        return bool(lock_time and datetime.now(timezone.utc) >= lock_time)

    def save_champion_prediction(self, user, chat_id: int | None, champion: str) -> None:
        champion = " ".join(champion.strip().split())
        if len(champion) < 2:
            raise ValueError("Вкажи назву збірної.")
        if len(champion) > 60:
            raise ValueError("Назва збірної занадто довга.")
        if self.is_champion_locked():
            raise ValueError("Прогноз чемпіона вже закрито.")
        team = self.find_world_cup_team_by_name(champion)
        if not team:
            raise ValueError("Не знайшов таку збірну серед учасників ЧС-2026.")

        self.save_champion_prediction_for_team(user, chat_id, team)

    def save_champion_prediction_by_team_id(self, user, chat_id: int | None, team_id: int) -> None:
        if self.is_champion_locked():
            raise ValueError("Прогноз чемпіона вже закрито.")
        team = self.find_world_cup_team_by_id(team_id)
        if not team:
            raise ValueError("Не знайшов таку збірну серед учасників ЧС-2026.")

        self.save_champion_prediction_for_team(user, chat_id, team)

    def save_champion_prediction_for_team(self, user, chat_id: int | None, team: dict[str, Any]) -> None:
        self.register_participant(user, chat_id)
        predictions = self.champion_predictions()
        try:
            team_id = int(team["api_football_team_id"])
        except (KeyError, TypeError, ValueError) as exc:
            raise ValueError("Для цієї збірної не вказано API-Football ID.") from exc
        champion_name_uk = team.get("name_uk") or team.get("name")
        champion_name = team.get("name") or champion_name_uk
        predictions[str(user.id)] = {
            "champion_team_id": team_id,
            "champion": champion_name_uk,
            "champion_name": champion_name,
            "champion_name_uk": champion_name_uk,
            "created_at": predictions.get(str(user.id), {}).get("created_at")
            or datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }
        self._write_json(CHAMPION_PREDICTIONS_FILE, predictions)

    def user_champion_prediction(self, user_id: int) -> dict[str, Any] | None:
        return self.champion_predictions().get(str(user_id))

    def save_prediction(
            self,
            user,
            chat_id: int | None,
            fixture_id: int,
            home_score: int,
            away_score: int,
    ) -> None:
        match = self.find_match(fixture_id)

        if not match:
            raise ValueError("Матч не знайдено.")

        if not self.is_match_resolved(match):
            raise ValueError("Команди цього матчу ще не визначені.")

        if self.is_locked(match):
            raise ValueError("Прийом прогнозів на цей матч уже закрито.")

        if home_score < 0 or away_score < 0 or home_score > 20 or away_score > 20:
            raise ValueError("Рахунок має бути в межах від 0 до 20.")

        self.register_participant(user, chat_id)

        user_predictions = self.user_predictions(user.id)

        user_predictions[str(fixture_id)] = {
            "fixture_id": fixture_id,
            "home_score": home_score,
            "away_score": away_score,
            "created_at": user_predictions.get(str(fixture_id), {}).get("created_at")
                          or datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }

        self._write_json(
            self._prediction_file(user.id),
            user_predictions,
        )

    def user_prediction(self, user_id: int, fixture_id: int) -> dict[str, Any] | None:
        return self.predictions().get(str(user_id), {}).get(str(fixture_id))

    def user_predictions(self, user_id: int) -> dict[str, dict[str, Any]]:
        path = self._prediction_file(user_id)

        if path.exists():
            return self._read_json(path, {})

        # fallback на старий формат
        return self.predictions().get(str(user_id), {})

    def match_predictions(self, fixture_id: int, include_private: bool = False) -> list[dict[str, Any]]:
        match = self.find_match(fixture_id)
        match_finished = bool(match and match.get("score_home") is not None and match.get("score_away") is not None)
        if not include_private and not match_finished:
            return []

        result = []
        participants = self.participants()
        for user_id, user_predictions in self.predictions().items():
            prediction = user_predictions.get(str(fixture_id))
            if prediction:
                result.append(
                    {
                        **prediction,
                        "user_id": int(user_id),
                        "display_name": participants.get(user_id, {}).get("display_name_b", f"User {user_id}"),
                    }
                )
        return result

    def public_match_predictions(self, fixture_id: int) -> list[dict[str, Any]]:
        return self.match_predictions(fixture_id)

    def _outcome(self, home_score: int, away_score: int) -> str:
        if home_score > away_score:
            return "home"
        if home_score < away_score:
            return "away"
        return "draw"

    def score_prediction(
        self,
        prediction: dict[str, Any],
        match: dict[str, Any],
        total_predictions: int,
        exact_predictions: int,
    ) -> ScoreResult:
        if match.get("score_home") is None or match.get("score_away") is None:
            return ScoreResult(0, False, False, False)

        actual_home = int(match["score_home"])
        actual_away = int(match["score_away"])
        predicted_home = int(prediction["home_score"])
        predicted_away = int(prediction["away_score"])

        correct_outcome = self._outcome(predicted_home, predicted_away) == self._outcome(actual_home, actual_away)
        exact = predicted_home == actual_home and predicted_away == actual_away
        rare_exact = exact and exact_predictions == 1

        points = 0
        if correct_outcome:
            points += 3
        if exact:
            points += 2
        if rare_exact:
            points += 2

        return ScoreResult(points, exact, correct_outcome, rare_exact)

    def standings(self) -> list[dict[str, Any]]:
        participants = self.participants()
        predictions = self.predictions()
        champion_predictions = self.champion_predictions()
        tournament_champion = self.tournament_champion()
        matches = self.matches()
        matches_by_id = {str(m["fixture_id"]): m for m in matches}
        rows = []

        for user_id, participant in participants.items():
            points = exact = correct = rare = zero = played = 0
            user_predictions = predictions.get(user_id, {})
            for fixture_id, prediction in user_predictions.items():
                match = matches_by_id.get(fixture_id)
                if not match or match.get("score_home") is None or match.get("score_away") is None:
                    continue

                match_predictions = self.match_predictions(int(fixture_id), include_private=True)
                total_predictions = len(match_predictions)
                exact_predictions = sum(
                    1
                    for p in match_predictions
                    if p["home_score"] == match["score_home"] and p["away_score"] == match["score_away"]
                )
                score = self.score_prediction(prediction, match, total_predictions, exact_predictions)
                points += score.points
                exact += int(score.exact)
                correct += int(score.correct_outcome)
                rare += int(score.rare_exact)
                zero += int(score.points == 0)
                played += 1

            champion_prediction = champion_predictions.get(user_id, {})
            champion_team_id = champion_prediction.get("champion_team_id")
            champion = champion_prediction.get("champion")
            tournament_champion_id = tournament_champion.get("api_football_team_id") if tournament_champion else None
            tournament_champion_name = tournament_champion.get("name_uk") or tournament_champion.get("name") if tournament_champion else None
            champion_hit = bool(
                (champion_team_id is not None and tournament_champion_id is not None and int(champion_team_id) == int(tournament_champion_id))
                or (
                    champion
                    and tournament_champion_name
                    and champion.strip().casefold() == tournament_champion_name.casefold()
                )
            )
            champion_points = 10 if champion_hit else 0
            points += champion_points
            rows.append(
                {
                    "user_id": int(user_id),
                    "display_name": participant.get("display_name_b", f"User {user_id}"),
                    "points": points,
                    "exact": exact,
                    "correct": correct,
                    "rare": rare,
                    "zero": zero,
                    "played": played,
                    "predictions_made": len(user_predictions),
                    "matches_total": len(matches),
                    "champion": champion,
                    "has_champion": bool(champion),
                    "champion_points": champion_points,
                    "champion_hit": champion_hit,
                    "champion_resolved": bool(tournament_champion),
                }
            )

        standings = sorted(rows, key=lambda r: (-r["points"], -r["champion_points"], -r["rare"], -r["exact"], -r["correct"], -r["predictions_made"], r["display_name"].lower()))
        self._save_leader(standings[0] if standings else None)
        return standings

    def _save_leader(self, leader: dict[str, Any] | None) -> None:
        tournament = self.tournament()
        tournament["leader"] = (
            {
                "user_id": leader["user_id"],
                "display_name": leader["display_name"],
                "points": leader["points"],
                "updated_at": datetime.now(timezone.utc).isoformat(),
            }
            if leader
            else None
        )
        self._write_json(TOURNAMENT_FILE, tournament)

    def due_reminders(self, now: datetime | None = None) -> list[dict[str, Any]]:
        now = now or datetime.now(timezone.utc)
        reminders_state = self._read_json(REMINDERS_FILE, {"sent": []})
        sent = set(reminders_state.get("sent", []))
        due = []

        first_match = self.first_match()
        if first_match:
            start = self.kickoff(first_match)
            champion_candidates = []
            for minutes in self.champion_reminder_minutes_before_start:
                key = f"champion:{minutes}"
                send_at = start - timedelta(minutes=minutes)
                if key not in sent and send_at <= now < start:
                    champion_candidates.append((minutes, key))
            if champion_candidates:
                minutes, key = min(champion_candidates, key=lambda item: item[0])
                due.append(
                    {
                        "key": key,
                        "type": "champion",
                        "fixture_id": None,
                        "text": (
                            "<b>🏆 Прогноз чемпіона ЧС-2026</b>\n\n"
                            f"Не забудьте обрати переможця турніру до початку першого матчу: {self._format_dual_dt(start)}. "
                            "Після старту першої гри прогноз чемпіона буде закрито."
                        ),
                    }
                )

        for match in self.matches():
            if not self.is_match_resolved(match):
                continue

            lock_time = self.lock_time(match)
            if now >= lock_time:
                continue
            match_candidates = []
            for minutes in self.match_reminder_minutes_before_lock:
                key = f"match:{match['fixture_id']}:{minutes}"
                send_at = lock_time - timedelta(minutes=minutes)
                if key not in sent and send_at <= now < lock_time:
                    match_candidates.append((minutes, key))
            if match_candidates:
                minutes, key = min(match_candidates, key=lambda item: item[0])
                due.append(
                    {
                        "key": key,
                        "type": "match",
                        "fixture_id": match["fixture_id"],
                        "text": (
                            f"<b>⏰ Нагадування про прогноз</b>\n\n"
                            f"{match.get('home_uk') or match['home']} - {match.get('away_uk') or match['away']}\n"
                            f"Початок: {self._format_dual_dt(self.kickoff(match))}\n"
                            f"Прогноз закривається за 90 хвилин до старту матчу."
                        ),
                    }
                )
        return due

    def mark_reminders_sent(self, keys: list[str]) -> None:
        if not keys:
            return
        reminders_state = self._read_json(REMINDERS_FILE, {"sent": []})
        sent = set(reminders_state.get("sent", []))
        sent.update(keys)
        self._write_json(REMINDERS_FILE, {"sent": sorted(sent)})

    def sync_results_from_api_day(self, raw: dict[str, Any]) -> int:
        api_matches = raw.get("response", []) if isinstance(raw, dict) else []
        if not api_matches:
            return 0
        api_matches = [match for match in api_matches if self._is_world_cup_api_match(match)]
        if not api_matches:
            return 0

        matches = self.matches()
        updated = 0
        for match in matches:
            api_match = self._find_api_match_for_schedule_match(match, api_matches)
            if not api_match:
                continue

            fixture = api_match.get("fixture") or {}
            venue = fixture.get("venue") or {}
            teams = api_match.get("teams") or {}
            goals = api_match.get("goals") or {}
            status = fixture.get("status") or {}
            home_team = teams.get("home") or {}
            away_team = teams.get("away") or {}
            home_known = self.find_world_cup_team_by_id(home_team.get("id"))
            away_known = self.find_world_cup_team_by_id(away_team.get("id"))

            changed = False
            updates = {
                "api_fixture_id": fixture.get("id"),
                "status": status.get("short") or match.get("status"),
                "home": home_team.get("name") or match.get("home"),
                "home_uk": (home_known or {}).get("name_uk") or match.get("home_uk"),
                "away": away_team.get("name") or match.get("away"),
                "away_uk": (away_known or {}).get("name_uk") or match.get("away_uk"),
                "home_team_id": home_team.get("id") or match.get("home_team_id"),
                "away_team_id": away_team.get("id") or match.get("away_team_id"),
                "venue": venue.get("name") or match.get("venue"),
                "score_home": goals.get("home"),
                "score_away": goals.get("away"),
            }
            for key, value in updates.items():
                if value is not None and match.get(key) != value:
                    match[key] = value
                    changed = True

            if changed:
                updated += 1

        if updated:
            self._write_json(MATCHES_FILE, matches)
        return updated

    def _find_api_match_for_schedule_match(self, match: dict[str, Any], api_matches: list[dict[str, Any]]) -> dict[str, Any] | None:
        api_fixture_id = match.get("api_fixture_id")
        if api_fixture_id:
            for api_match in api_matches:
                if (api_match.get("fixture") or {}).get("id") == api_fixture_id:
                    return api_match

        home_team_id = match.get("home_team_id")
        away_team_id = match.get("away_team_id")
        if home_team_id and away_team_id:
            for api_match in api_matches:
                teams = api_match.get("teams") or {}
                home = teams.get("home") or {}
                away = teams.get("away") or {}
                if home.get("id") == home_team_id and away.get("id") == away_team_id:
                    return api_match

        scheduled_at = self.kickoff(match)
        for api_match in api_matches:
            fixture = api_match.get("fixture") or {}
            date_value = fixture.get("date")
            if not date_value:
                continue
            try:
                api_kickoff = datetime.fromisoformat(date_value.replace("Z", "+00:00"))
            except ValueError:
                continue
            if abs((api_kickoff - scheduled_at).total_seconds()) <= 15 * 60:
                return api_match
        return None

    def _is_world_cup_api_match(self, api_match: dict[str, Any]) -> bool:
        league = api_match.get("league") or {}
        return int(league.get("id") or 0) == 1 and int(league.get("season") or 0) == 2026
