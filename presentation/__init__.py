from .controllers.main_menu import router as main_menu_router
from presentation.controllers.detail import router as detail_router
from presentation.controllers.lineups import router as lineups_router
from presentation.controllers.navigation import router as navigation_router
from presentation.controllers.teams import router as teams_router
from presentation.controllers.players import router as players_router

all_routers = [
    main_menu_router,
    detail_router,
    lineups_router,
    navigation_router,
    teams_router,
    players_router,
]
