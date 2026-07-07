# application/services/news_digest_service.py
from datetime import date, datetime, timedelta
from typing import List

from domain.models.match import Match
from application.services.team_service import is_ukrainian_team, is_selected_team, highlight_team
from application.api.youtube_service import search_match_highlight
from data.icons import ICONS
from data.selected_teams import WORLD_CUP_END, WORLD_CUP_START


def _is_world_cup_period(day: date | None = None) -> bool:
    day = day or date.today()
    return WORLD_CUP_START <= day <= WORLD_CUP_END


def _format_match_time(date_utc: str) -> str:
    from config import TZ_ITALY, TZ_UKRAINE

    dt = datetime.fromisoformat(date_utc.replace("Z", "+00:00"))
    italy = dt.astimezone(TZ_ITALY).strftime("%d.%m %H:%M")
    ukraine = dt.astimezone(TZ_UKRAINE).strftime("%d.%m %H:%M")
    return f"{italy} {ICONS['it_flag']} / {ukraine} {ICONS['ua_flag']}"

class NewsDigestService:
    def __init__(self, repo, player_performance):
        self.repo = repo
        self.player_performance = player_performance

    async def generate_yesterday_digest(self) -> str:
        if _is_world_cup_period():
            return self.generate_world_cup_digest()

        yesterday = date.today() - timedelta(days=1)
        matches: List[Match] = await self.repo.list_matches_for_day(yesterday)

        if not matches:
            return (
                f"{ICONS['news']} Вчора не було матчів за участю відстежуваних клубів чи гравців.\n\n"
                "Перейдіть до розділу «Матчі», щоб переглянути розклад на сьогодні та завтра."
            )

        lines = [f"{ICONS['news']} Ранковий дайджест за {yesterday.strftime('%d.%m.%Y')}\n"]

        for match in matches:

            score = (f"Матч між {highlight_team(match.home)} та {highlight_team(match.away)} завершився з рахунком "
                     f"{match.score_home or 0}–{match.score_away or 0}")

            home_selected_foreign = is_selected_team(match.home_id) and not is_ukrainian_team(match.home_id)
            away_selected_foreign = is_selected_team(match.away_id) and not is_ukrainian_team(match.away_id)

            if home_selected_foreign or away_selected_foreign:
                lines.append(f"  {score}")

                teams_to_analyze = []
                if home_selected_foreign:
                    teams_to_analyze.append((match.home_id, match.home))
                if away_selected_foreign:
                    teams_to_analyze.append((match.away_id, match.away))

                for team_id, team_name in teams_to_analyze:
                    lines.append(f"В складі команди {highlight_team(team_name)}:")

                    from data.selected_teams import TEAMS
                    team_data = TEAMS.get(team_id)
                    if not team_data or not team_data.get("players"):
                        lines.append(" немає відстежуваних гравців")
                        continue

                    ukr_players = team_data["players"]

                    for p_id, p_name in ukr_players.items():
                        perf = await self.player_performance.get_player_info(match, p_id, p_name, team_id)

                        if not perf["in_squad"]:
                            lines.append(f"   {ICONS['ua_flag']} {p_name}: не потрапив навіть у заявку")
                            continue

                        status = perf["status"]
                        actions = perf["actions"]

                        if actions:
                            actions_text = f", запам'ятався: {', '.join(actions)}"
                        else:
                            actions_text = ", без результативних дій" if "провів" in status or "замінений" in status else ""

                        lines.append(f"    {ICONS['ua_flag']} {p_name}: {status}{actions_text}")

                video_url = await search_match_highlight(match)
                if video_url:
                    lines.append(f"📹 <a href='{video_url}'>Відеоогляд матчу</a>")

                    if match.video_url == video_url:
                        pass
                    else:
                        match.video_url = video_url
                        await self.repo.save_match(match)  #
            else:
                lines.append(f"• {score}")

            lines.append("")

        lines.append("\nДетальніше — у розділі матчів")
        return "\n".join(lines)

    def generate_world_cup_digest(self) -> str:
        from application.services.predictions import PredictionService

        svc = PredictionService()
        today = date.today()
        sections = [
            ("Вчора", today - timedelta(days=1)),
            ("Сьогодні", today),
            ("Завтра", today + timedelta(days=1)),
        ]
        lines = [f"{ICONS['news']} Дайджест ЧС-2026\n"]

        for title, day in sections:
            matches = svc.matches_on_utc_date(day)
            lines.append(f"<b>{title} · {day.strftime('%d.%m.%Y')}</b>")
            if not matches:
                lines.append("Матчів немає.\n")
                continue

            for match in matches:
                score = ""
                if match.get("score_home") is not None and match.get("score_away") is not None:
                    score = f" <b>{match['score_home']}:{match['score_away']}</b>"
                status = f" · {match.get('status')}" if match.get("status") and match.get("status") != "NS" else ""
                lines.append(
                    f"• {match.get('home_uk') or match['home']} - {match.get('away_uk') or match['away']}"
                    f"{score}{status}\n"
                    f"  {match.get('group') or match.get('stage')} · {_format_match_time(match['date_utc'])}"
                )
            lines.append("")

        return "\n".join(lines)
