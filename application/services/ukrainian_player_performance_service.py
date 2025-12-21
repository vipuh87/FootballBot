# application/services/ukrainian_player_performance_service.py
from typing import List, Dict
from domain.models.match import Match

class UkrainianPlayerPerformanceService:
    async def get_player_info(self, match: Match, player_id: int, player_name: str, team_id: int) -> Dict:
        in_squad = self._player_in_squad(match, player_id, team_id)
        if not in_squad:
            return {"in_squad": False, "status": "Не в заявці", "actions": []}

        status = self._get_play_status(match, player_id)
        actions = self._player_actions(match, player_id)

        return {
            "in_squad": True,
            "status": status,
            "actions": actions,
            "name": player_name
        }

    def _player_in_squad(self, match: Match, player_id: int, team_id: int) -> bool:
        if not match.lineups:
            return False
        for lineup in match.lineups:
            if lineup.get("team", {}).get("id") == team_id:
                all_players = lineup.get("startXI", []) + lineup.get("substitutes", [])
                return any(p.get("player", {}).get("id") == player_id for p in all_players)
        return False

    def _get_play_status(self, match: Match, player_id: int) -> str:
        in_start = False
        sub_in_time = None
        sub_out_time = None

        if match.lineups:
            for lineup in match.lineups:
                for p in lineup.get("startXI", []):
                    if p.get("player", {}).get("id") == player_id:
                        in_start = True

        if match.events:
            for e in match.events:
                if e.get("type") == "subst":
                    if e.get("player", {}).get("id") == player_id:  # Замінений (вийшов)
                        sub_out_time = e["time"]["elapsed"]
                    if e.get("assist", {}).get("id") == player_id:  # Вийшов на заміну
                        sub_in_time = e["time"]["elapsed"]

        if in_start:
            if sub_out_time:
                return f"Вийшов у старті, замінений на {sub_out_time}'"
            return "Вийшов у старті, провів весь матч"
        elif sub_in_time:
            if sub_out_time:
                return f"Вийшов на заміну на {sub_in_time}', замінений на {sub_out_time}'"
            return f"Вийшов на заміну на {sub_in_time}'"
        return "Залишився в запасі"

    def _player_actions(self, match: Match, player_id: int) -> List[str]:
        actions = []
        if match.events:
            for e in match.events:
                player_match = e.get("player", {}).get("id") == player_id
                assist_match = e.get("assist", {}).get("id") == player_id

                time = e["time"]["elapsed"]
                extra = e["time"].get("extra")
                time_str = f"{time}'" + (f"+{extra}'" if extra else "")

                if e.get("type") == "Goal":
                    if player_match:
                        detail = e.get("detail", "")
                        goal_type = " (пен.)" if "Penalty" in detail else " (автогол)" if "Own Goal" in detail else ""
                        actions.append(f"гол {time_str}{goal_type}")
                    if assist_match:
                        actions.append(f"асист {time_str}")

                elif e.get("type") == "Card" and player_match:
                    card = "ЖК" if "Yellow" in e.get("detail", "") else "ЧК"
                    actions.append(f"{card} {time_str}")
        return actions