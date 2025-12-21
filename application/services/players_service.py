from application.services.team_service import is_selected_team, is_ukrainian_team
from application.services.lineup_service import get_lineups
from application.services.team_service import get_team


def get_selected_players_by_team(team):
    return team[1].get("players")

async def get_ukrainian_players_for_match(match):
    lineups = await get_lineups(match)

    if not lineups or not isinstance(lineups, list):
        return []

    result = []

    for lineup in lineups:
        team = lineup.get("team", {})
        team_id = team.get("id")
        team_name = team.get("name")

        if not is_selected_team(team_id) or is_ukrainian_team(team_id):
            continue

        ukrainian_players = get_players_for_team(team_id)
        ukrainian_ids = set(ukrainian_players)

        start_players = []
        sub_players = []

        for p in lineup.get("startXI", []):
            player = p.get("player", {})
            if player.get("id") in ukrainian_ids:
                start_players.append(player)

        for p in lineup.get("substitutes", []):
            player = p.get("player", {})
            if player.get("id") in ukrainian_ids:
                sub_players.append(player)

        if start_players or sub_players:
            result.append({
                "team_id": team_id,
                "team_name": team_name,
                "start": start_players,
                "subs": sub_players,
            })

    return result

def get_players_for_team(team_id: int) -> list:
    team = get_team(team_id)
    if not team:
        return []
    return team.get("players", [])