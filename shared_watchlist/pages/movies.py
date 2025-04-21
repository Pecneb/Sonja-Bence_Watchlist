import solara
import pandas as pd
from typing import Optional
from components.appbar import AppBar


@solara.component
def Page():
    """
    Movies Page for adding movies manually or importing via CSV.
    """
    # State variables for movie metadata
    title = solara.use_reactive("")
    director = solara.use_reactive("")
    year = solara.use_reactive("")
    genre = solara.use_reactive("")
    csv_file = solara.use_reactive(None)
    message = solara.use_reactive("")

    # Shared AppBar
    AppBar()

    def add_movie():
        """
        Add a movie manually using the entered metadata.
        """
        if not title.value or not year.value:
            message.set("Title and Year are required fields!")
            return
        # Simulate adding the movie to the database
        message.set(f"Movie '{title.value}' added successfully!")

    def import_csv(file):
        """
        Import movies from a CSV file.
        """
        try:
            df = pd.read_csv(file)
            # Simulate adding movies to the database
            message.set(f"Imported {len(df)} movies successfully!")
        except Exception as e:
            message.set(f"Error importing CSV: {str(e)}")

    solara.Markdown(
        """
    # Add Movies 🎥

    You can add movies to your collection by:
    - Manually entering the movie metadata.
    - Importing a CSV file with movie details.
    """
    )

    # Form for manual movie entry
    with solara.Card("Add Movie Manually"):
        solara.InputText("Title", value=title, on_value=title.set)
        solara.InputText("Director", value=director, on_value=director.set)
        solara.InputText("Year", value=year, on_value=year.set)
        solara.InputText("Genre", value=genre, on_value=genre.set)
        solara.Button("Add Movie", on_click=add_movie)

    # File upload for CSV import
    with solara.Card("Import Movies from CSV"):
        solara.FileDrop(on_file=import_csv, label="Upload CSV File")

    # Display messages
    if message.value:
        solara.Success(
            message.value,
            color="success" if "successfully" in message.value else "error",
        )
