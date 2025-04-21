import solara
from solara import Reactive
from typing import List
from components.appbar import AppBar
from auth.auth import get_current_user, LoginButton
from utils.database.wathclist import Watchlist, WatchlistItem
from utils.database.movies import Movie

@solara.component
def SearchForMovieComponent(results: Reactive[List[Movie]]):
    pass

@solara.component
def WatchlistComponent(watchlists: Reactive[List[Watchlist]]):
    pass

@solara.component
def Page():
    """
    Watchlist Page for creating, editing, and sharing watchlists.
    """
    # State variables
    watchlist_name = solara.use_reactive("")
    watchlists = solara.use_reactive([])  # List of watchlists
    selected_watchlist = solara.use_reactive(None)
    shared_with = solara.use_reactive("")
    message = solara.use_reactive("")

    # Shared AppBar
    AppBar()

    with solara.Column(align="center"):
        if not get_current_user():
            solara.Markdown("# Please Log In before accessing the application!")
            LoginButton()
            return

    def create_watchlist():
        """
        Create a new watchlist.
        """
        if not watchlist_name.value:
            message.set("Watchlist name is required!")
            return
        new_watchlist = {
            "name": watchlist_name.value,
            "movies": [],
            "shared_with": [],
        }
        watchlists.value = list(watchlists.value) + [new_watchlist]
        watchlist_name.set("")
        message.set(f"Watchlist '{new_watchlist['name']}' created successfully!")

    def edit_watchlist(watchlist):
        """
        Select a watchlist for editing.
        """
        selected_watchlist.set(watchlist)

    def update_watchlist():
        """
        Update the selected watchlist.
        """
        if selected_watchlist.value:
            selected_watchlist.value["name"] = watchlist_name.value
            watchlist_name.set("")
            selected_watchlist.set(None)
            message.set("Watchlist updated successfully!")

    def share_watchlist():
        """
        Share the selected watchlist with another user.
        """
        if selected_watchlist.value and shared_with.value:
            selected_watchlist.value["shared_with"].append(shared_with.value)
            shared_with.set("")
            message.set(f"Watchlist shared with {shared_with.value}!")

    with solara.Column(align="center"):
        solara.Markdown(
            """
        # Manage Your Watchlists 🎥

        Create, edit, and share your movie watchlists with others.
        """
        )

    with solara.Columns(widths=(4,8)):
        # Form to create or edit a watchlist
        with solara.Card("Create or Edit Watchlist"):
            solara.InputText(
                "Watchlist Name", value=watchlist_name, on_value=watchlist_name.set
            )
            if selected_watchlist.value:
                solara.Button("Update Watchlist", on_click=update_watchlist)
            else:
                solara.Button("Create Watchlist", on_click=create_watchlist)

        # List of watchlists
        with solara.Card("Your Watchlists"):
            if not watchlists.value:
                solara.Markdown("You have no watchlists yet.")
            else:
                for watchlist in watchlists.value:
                    with solara.Card(watchlist["name"]):
                        solara.Markdown(
                            f"**Movies**: {', '.join(watchlist['movies']) or 'None'}"
                        )
                        solara.Markdown(
                            f"**Shared With**: {', '.join(watchlist['shared_with']) or 'None'}"
                        )
                        solara.Button(
                            "Edit", on_click=lambda w=watchlist: edit_watchlist(w)
                        )
                        solara.Button(
                            "Share", on_click=lambda w=watchlist: selected_watchlist.set(w)
                        )

        # Form to share a watchlist
        if selected_watchlist.value:
            with solara.Card(f"Share Watchlist: {selected_watchlist.value['name']}"):
                solara.InputText(
                    "Share With (User Email)", value=shared_with, on_value=shared_with.set
                )
                solara.Button("Share", on_click=share_watchlist)

        # Display messages
        if message.value:
            solara.Success(
                message.value,
                color="success" if "successfully" in message.value else "error",
            )
