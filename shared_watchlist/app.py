import pandas as pd
import solara
from pathlib import Path
from database import init_db, get_db_connection

# from auth import with_authentication

# Initialize the database
init_db()


refresh_trigger = solara.reactive(0)


@solara.component
# @with_authentication
def AddMovie():
    title = solara.use_reactive("")
    year = solara.use_reactive("")
    error_msg = solara.use_reactive("")

    def handle_add():
        if len(title.get()) == 0 or len(year.get()) == 0:
            error_msg.set("Title or Year missing!")
            return
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO watchlist (title, year, added_by) VALUES (?, ?, ?)",
                (title.value, year.value, "User"),
            )
            conn.commit()
        error_msg.set("")
        title.set("")
        year.set("")
        refresh_trigger.set(refresh_trigger.value + 1)

    with solara.Column():
        solara.InputText(label="Movie Title", value=title)
        solara.InputText(label="Release Year", value=year)
        solara.Button(label="Add to Watchlist", on_click=handle_add)
        if len(error_msg.get()) > 0:
            solara.Error(error_msg.get())


@solara.component
# @with_authentication
def Watchlist():
    # Access the trigger to establish dependency
    _ = refresh_trigger.value

    # Fetch the current watchlist from the database
    with get_db_connection() as conn:
        df = pd.read_sql_query("SELECT * FROM watchlist", conn)

    # Define the delete function
    def delete_movie(row_index):
        movie_id = df.iloc[row_index]["id"]
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM watchlist WHERE id = ?", (movie_id,))
            conn.commit()
        refresh_trigger.value += 1  # Trigger refresh

    # Define the cell action for deletion
    cell_actions = [
        solara.CellAction(
            name="Delete",
            icon="mdi-delete",
            on_click=lambda column, row_index: delete_movie(row_index),
        )
    ]

    # Display the DataFrame with cell actions
    solara.DataFrame(df, cell_actions=cell_actions)


# Load the dataset
df_movies = pd.read_csv(Path(__file__).parent / "data/movies.csv")


@solara.component
def MovieSearch():
    # Reactive state for the search query
    search_query = solara.use_reactive("")

    # Filter the DataFrame based on the search query
    if search_query.value:
        # Perform case-insensitive search across specified columns
        mask = df_movies.apply(
            lambda row: row[
                ["title", "genres", "overview", "tagline", "cast", "crew", "director"]
            ]
            .astype(str)
            .str.contains(search_query.value, case=False, na=False)
            .any(),
            axis=1,
        )
        filtered_df = df_movies[mask]
    else:
        filtered_df = df_movies

    # Layout the components
    with solara.Column():
        solara.InputText(
            "Search movies",
            value=search_query,
            # on_value=set_search_query,
            continuous_update=True,
        )
        solara.DataFrame(
            filtered_df[["title", "genres", "release_date"]], items_per_page=10
        )


@solara.component
def Page():
    with solara.Column():
        AddMovie()
        Watchlist()
        MovieSearch()
        solara.lab.ThemeToggle()
