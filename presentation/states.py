# presentation/states.py
from aiogram.fsm.state import State, StatesGroup

class BotStates(StatesGroup):
    main_menu = State()          # головне меню
    day_view = State()           # список матчів за день (зберігаємо day_offset)
    match_detail = State()       # деталі матчу (зберігаємо fixture_id)
    lineups = State()            # склади (зберігаємо fixture_id + side: "home"/"away")
    lineups_menu = State()       # меню вибору команди для складів
    lineup_team = State()        # перегляд конкретного складу (home/away)
    events = State()             # події матчу
    stats = State()              # статистика матчу
    players = State()            # українські гравці (якщо окрема секція)
    teams = State()              # українські гравці (якщо окрема секція)

