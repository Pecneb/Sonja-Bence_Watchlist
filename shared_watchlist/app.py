import solara
from pages import home, movies, watchlist
from auth.auth import AuthAvatarMenu

routes = [
    solara.Route(path="/", component=home.Page, label="Home"),
    # solara.Route(path="movies", component=movies.Page, label="Movies"),
    solara.Route(path="watchlists", component=watchlist.Page, label="Watchlists"),
]
