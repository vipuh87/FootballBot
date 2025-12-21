# application/services/news_digest_service.py
from datetime import date, timedelta
from typing import List

from domain.models.match import Match
from application.services.team_service import is_ukrainian_team, is_selected_team, highlight_team

class NewsDigestService:
    def __init__(self, repo, player_performance):
        self.repo = repo
        self.player_performance = player_performance

    async def generate_yesterday_digest(self) -> str:
        yesterday = date.today() - timedelta(days=1)
        matches: List[Match] = await self.repo.list_matches_for_day(yesterday)

        if not matches:
            return (
                "📰 Вчора не було матчів за участю відстежуваних клубів чи гравців.\n\n"
                "Перейдіть до розділу «Матчі», щоб переглянути розклад на сьогодні."
            )

        lines = [f"📊 Результати вчора ({yesterday.strftime('%d %m %Y')})\n"]

        for match in matches:
            score = f"{highlight_team(match.home)} {match.score_home or 0}–{match.score_away or 0} {highlight_team(match.away)}"

            home_selected_foreign = is_selected_team(match.home_id) and not is_ukrainian_team(match.home_id)
            away_selected_foreign = is_selected_team(match.away_id) and not is_ukrainian_team(match.away_id)

            if home_selected_foreign or away_selected_foreign:
                lines.append(f"• {score}")

                teams_to_analyze = []
                if home_selected_foreign:
                    teams_to_analyze.append((match.home_id, match.home))
                if away_selected_foreign:
                    teams_to_analyze.append((match.away_id, match.away))

                for team_id, team_name in teams_to_analyze:
                    lines.append(f"  🇺🇦 {team_name}:")

                    from data.selected_teams import TEAMS
                    team_data = TEAMS.get(team_id)
                    if not team_data or not team_data.get("players"):
                        lines.append("    (немає відстежуваних гравців)")
                        continue

                    ukr_players = team_data["players"]  # {id: name}

                    for p_id, p_name in ukr_players.items():
                        perf = await self.player_performance.get_player_info(match, p_id, p_name, team_id)

                        if not perf["in_squad"]:
                            lines.append(f"    • {p_name}: не в заявці")
                            continue

                        status = perf["status"]
                        actions = perf["actions"]

                        if actions:
                            actions_text = f", запам'ятався: {', '.join(actions)}"
                        else:
                            actions_text = ", без результативних дій" if "провів" in status or "замінений" in status else ""

                        lines.append(f"    • {p_name}: {status}{actions_text}")
            else:
                lines.append(f"• {score}")

            lines.append("")  # відступ між матчами

        lines.append("\nДетальніше — у розділі матчів")
        return "\n".join(lines)