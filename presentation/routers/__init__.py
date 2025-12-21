from .main_menu_router import router as main_menu_router
from .matches_router import router as matches_router
# from .teams_router import router as teams_router
# from .players_router import router as players_router
# from .match_details_router import router as match_details_router

all_routers = [
    main_menu_router,
    matches_router,
    # teams_router,
    # players_router,
    # match_details_router,
]