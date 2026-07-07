from aiogram.fsm.state import State, StatesGroup


class BotStates(StatesGroup):
    main_menu = State()
    day_view = State()
    match_detail = State()
    lineups = State()
    lineups_menu = State()
    lineup_team = State()
    events = State()
    stats = State()
    players = State()
    teams = State()
    prediction_manual_score = State()
    prediction_champion = State()
