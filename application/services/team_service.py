from data.selected_teams import TEAMS, SELECTED_TEAM_IDS

def get_all_teams():
    return TEAMS.items()

def get_all_team_names() -> list[str]:
    return [team["name"] for team in TEAMS.values()]


def is_selected_team(team_id: int) -> bool:
    return team_id in SELECTED_TEAM_IDS


def get_team(team_id: int):
    return TEAMS.get(team_id)

def is_ukrainian_team(team_id: int) -> bool:
    team = get_team(team_id)
    return team.get("is_ukrainian", False) if team else False

def highlight_team(name: str) -> str:
    if name in get_all_team_names():
        return f"<b>{name}</b>"
    return name
