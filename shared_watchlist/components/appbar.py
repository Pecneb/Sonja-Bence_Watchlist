import sys
import os

import solara
from solara import lab
from auth.auth import AuthAvatarMenu


@solara.component
def AppBar():
    # Set the primary color to orange for both light and dark themes
    lab.theme.themes.light.primary = "#FF9800"  # Orange
    lab.theme.themes.dark.primary = "#FF9800"   # Orange
    with solara.AppBar():
        with solara.AppBarTitle():
            solara.Markdown("## The Watchlist")
        AuthAvatarMenu()
        lab.ThemeToggle()
        with lab.Tabs(color="black", align="center"):
            lab.Tab("Home", icon_name="mdi-home", path_or_route="/")
            # lab.Tab("Movies", icon_name="mdi-camera", path_or_route="/movies")
            lab.Tab("Watchlists", icon_name="mdi-eye", path_or_route="/watchlists")