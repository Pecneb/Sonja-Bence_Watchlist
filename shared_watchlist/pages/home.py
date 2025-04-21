import os
import sys

import solara
from components.appbar import AppBar
from auth.auth import get_current_user, LoginButton
from shared_data import user
from utils.database.users import User


@solara.component
def Page():
    """
    Welcome Page for the Movie Watchlist App.
    """
    AppBar()
    with solara.Column(align="center"):
        if not get_current_user():
            solara.Markdown("# Please Log In before accessing the application!")
            LoginButton()
            return
        user.value = User.from_oauth_response(get_current_user())
        solara.Markdown(
            """
        # Welcome to the Movie Watchlist App! 🎬

        This application allows you to:
        - Create and manage your personal movie watchlists.
        - Share your watchlists with friends and family.
        - Search for movies and add them to your watchlists.
        - Collaborate with others by setting permissions for shared watchlists.

        ## Features:
        - **User Authentication**: Securely log in to access your personalized watchlists.
        - **Movie Search**: Quickly find movies by title and add them to your lists.
        - **Sharing & Permissions**: Share your watchlists and control who can view or edit them.

        Get started by logging in or creating your first watchlist!
        """
        )
