import json
from datetime import date
from pathlib import Path


WORLD_CUP_START = date(2026, 6, 11)
WORLD_CUP_END = date(2026, 7, 19)


def _world_cup_tracking_enabled() -> bool:
    today = date.today()
    return WORLD_CUP_START <= today <= WORLD_CUP_END


def _load_world_cup_teams() -> dict[int, dict]:
    path = Path(__file__).resolve().parent / "predictions" / "world_cup_2026_teams.json"
    if not path.exists():
        return {}

    try:
        teams = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}

    result = {}
    for team in teams:
        try:
            team_id = int(team["api_football_team_id"])
        except (KeyError, TypeError, ValueError):
            continue
        result[team_id] = {
            "name": team.get("name") or team.get("name_uk") or f"Team {team_id}",
            "is_ukrainian": False,
            "youtube_channel_id": None,
            "players": {},
            "is_world_cup_2026": True,
        }
    return result


TEAMS = {
    572: {
        "name": "Dynamo Kyiv",
        "is_ukrainian": True,
        "youtube_channel_id": "UC0yD2Aw5-HOYUyZCu7hyR9Q",
        "players": {}
    },
    550:
        {
        "name": "Shakhtar Donetsk",
        "is_ukrainian": True,
        "youtube_channel_id": "UCmPCqUih--EyT2oxUn72Mt",
        "players": {}
    },
    85:
        {
        "name": "Paris Saint Germain",
        "is_ukrainian": False,
        "youtube_channel_id": "UCt9a_qP9CqHCNwilf-iULag",
        "players": {
            161671: "Ілля Забарний"
        }
    },
    497: {
        "name": "AS Roma",
        "is_ukrainian": False,
        "youtube_channel_id": "UCLttSYJ6kPtlcurY96kXkQw",
        "players": {
            15811: "Артем Довбик"
        }
    },
    211: {
        "name": "Benfica",
        "is_ukrainian": False,
        "youtube_channel_id": "UC8zrah5cNf2c3jKKeD_Z3fw",
        "players": {
            675: "Анатолій Трубін",
            161945: "Георгій Судаков"
        }
    },
    45: {
        "name": "Everton",
        "is_ukrainian": False,
        "youtube_channel_id": "UCtK4QAczAN2mt2ow_jlGinQ",
        "players": {
            2165: "Віталій Миколинко"
        }
    },
    65: {
        "name": "Nottingham Forest",
        "is_ukrainian": False,
        "youtube_channel_id": "UCyAxjuAr8f_BFDGCO3Htbxw",
        "players": {
            641: "Олександр Зінченко"
        }
    },
    495: {
        "name": "Genoa",
        "is_ukrainian": False,
        "youtube_channel_id": "UCcFYiZvNtDbvVak3wEj3usA",
        "players": {
            1938: "Руслан Маліновський"
        }
    },
    541: {
        "name": "Real Madrid",
        "is_ukrainian": False,
        "youtube_channel_id": "UCWV3obpZVGgJ3j9FVhEjF2Q",
        "players": {
            47400: "Андрій Лунін"
        }
    },
    547: {
        "name": "Girona",
        "is_ukrainian": False,
        "youtube_channel_id": "UC6x5gKUZpXuKDujmaHc3Xhg",
        "players": {
            161670: "Владислав Ванат",
            2182: "Віктор Циганков"
        }
    },
    55: {
        "name": "Brentford",
        "is_ukrainian": False,
        "youtube_channel_id": "UCAalMUm3LIf504ItA3rqfug",
        "players": {
            263538: "Єгор Ярмолюк"
        }
    },
    #553: {
    #    "name": "Olympiakos Piraeus",
    #    "is_ukrainian": False,
    #    "youtube_channel_id": "UCLf7YXb-0PWEeq59Z_q318A",
    #    "players": {
    #        8493: "Роман Яремчук"
    #    }
    #},
    6495: {
        "name": "Podillya Khmelnytskyi",
        "is_ukrainian": True,
        "youtube_channel_id": "UCLf7YXb-0PWEeq59Z_q318A",
        "players": {}
    },
    14434: {
        "name": "Epitsentr Dunayivtsi",
        "is_ukrainian": True,
        "youtube_channel_id": "UCHko6byc2wu-P82e5qGRQcw",
        "players": {}
    },
    772: {
        "name": "Ukraine",
        "is_ukrainian": True,
        "youtube_channel_id": "UC2lzyKjfyh3FN_f_iYmXlCA",
        "players": {}
    },
    23313: {
        "name": "Ukraine U23",
        "is_ukrainian": True,
        "youtube_channel_id": "UC2lzyKjfyh3FN_f_iYmXlCA",
        "players": {}
    },
    8228: {
        "name": "Ukraine U21",
        "is_ukrainian": True,
        "youtube_channel_id": "UC2lzyKjfyh3FN_f_iYmXlCA",
        "players": {}
    },
    10305: {
        "name": "Ukraine U20",
        "is_ukrainian": True,
        "youtube_channel_id": "UC2lzyKjfyh3FN_f_iYmXlCA",
        "players": {}
    },
    10352: {
        "name": "Ukraine U19",
        "is_ukrainian": True,
        "youtube_channel_id": "UC2lzyKjfyh3FN_f_iYmXlCA",
        "players": {}
    },
    22343: {
        "name": "Ukraine U18",
        "is_ukrainian": True,
        "youtube_channel_id": "UC2lzyKjfyh3FN_f_iYmXlCA",
        "players": {}
    },
    17983: {
        "name": "Ukraine U17",
        "is_ukrainian": True,
        "youtube_channel_id": "UC2lzyKjfyh3FN_f_iYmXlCA",
        "players": {}
    },
    489: {
        "name": "AC Milan",
        "is_ukrainian": False,
        "youtube_channel_id": "UCKcx1uK38H4AOkmfv4ywlrg",
        "players": {}
    },
    6486: {
        "name": "Bukovyna",
        "is_ukrainian": True,
        "youtube_channel_id": "UCq7zX_xulgwuukB1cXD4N3w",
        "players": {}
    },
    80: {
        "name": "Lyon",
        "is_ukrainian": False,
        "youtube_channel_id": "UCzHCZXmqIdjqRnpdp0l_T6g",
        "players": {
            8493: "Роман Яремчук"
        }
    },
}

BASE_SELECTED_TEAM_IDS = list(TEAMS.keys())
WORLD_CUP_TEAMS = _load_world_cup_teams()
WORLD_CUP_TEAM_IDS = list(WORLD_CUP_TEAMS.keys())
TEAMS.update({team_id: data for team_id, data in WORLD_CUP_TEAMS.items() if team_id not in TEAMS})


def get_selected_team_ids(day: date | None = None) -> list[int]:
    day = day or date.today()
    selected = list(BASE_SELECTED_TEAM_IDS)
    if WORLD_CUP_START <= day <= WORLD_CUP_END:
        selected.extend(team_id for team_id in WORLD_CUP_TEAM_IDS if team_id not in selected)
    return selected


SELECTED_TEAM_IDS = get_selected_team_ids()
