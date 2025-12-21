from domain.models.match import Match

async def get_lineups(match: Match):
    if match.lineups:
        return match.lineups

    from application.container import Container

    api = Container.get().api
    repo = Container.get().repo

    raw = await api.lineup_by_fixture(match.fixture_id)

    if not raw or not raw.get("response"):
        match.lineups = []
        return []

    lineups = raw["response"]
    match.lineups = lineups
    await repo.save_match(match)

    return lineups

def get_start_xi(team_data):
    return team_data.get("startXI", [])

def get_substitutes(team_data):
    return team_data.get("substitutes", [])