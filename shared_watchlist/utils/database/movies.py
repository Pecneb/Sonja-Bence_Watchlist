import re
from abc import ABC, abstractmethod
from typing import List, Optional

from pydantic import BaseModel, HttpUrl, PastDate, field_validator
from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.errors import DuplicateKeyError, PyMongoError
from tmdbv3api import Movie as TMDbMovie

from utils.database.db_config import db


class Movie(BaseModel):
    id: int
    title: str
    overview: Optional[str] = None
    release_date: Optional[PastDate] = None
    poster_path: Optional[HttpUrl] = None

    @field_validator("poster_path", mode="before")
    def prepend_base_url(cls, value: str) -> str:
        base_url = "https://image.tmdb.org/t/p/w500/"
        if not value.startswith(base_url):
            return f"{base_url}{value.lstrip('/')}"
        return value


class IMovieRepository(ABC):
    @abstractmethod
    def get_all_movies(self) -> List[Movie]:
        """Retrieve all movies from the database."""
        pass

    @abstractmethod
    def get_movie_by_id(self, movie_id: int) -> Optional[Movie]:
        """Retrieve a movie by its ID."""
        pass

    @abstractmethod
    def add_movie(self, movie: Movie) -> None:
        """Add a new movie to the database."""
        pass

    @abstractmethod
    def delete_movie(self, movie_id: int) -> None:
        """Delete a movie by its ID."""
        pass

    @abstractmethod
    def search_and_cache_movie(self, title: str) -> Optional[Movie]:
        """Fetch movie from TMDB API then cache in database."""
        pass

    @abstractmethod
    def fetch_recommendations(self) -> Optional[List[Movie]]:
        """Fetch a list of recommended movies."""
        pass


class MongoMovieRepository(IMovieRepository):
    def __init__(self, db_client: MongoClient, db_name: str, collection_name: str):
        self.collection: Collection = db_client[db_name][collection_name]
        self.tmdb_movie = TMDbMovie()

    def get_all_movies(self) -> List[Movie]:
        cursor = self.collection.find()
        return [Movie(**doc) for doc in cursor]

    def get_movie_by_id(self, movie_id: int) -> Optional[Movie]:
        movie = self.collection.find_one({"id": movie_id})
        return Movie(**movie) if movie else None

    def add_movie(self, movie: Movie) -> None:
        try:
            self.collection.insert_one(movie.dict())
        except DuplicateKeyError:
            pass  # Movie already exists

    def delete_movie(self, movie_id: int) -> None:
        try:
            result = self.collection.delete_one({"id": movie_id})
            if result.deleted_count == 0:
                raise ValueError(f"Movie with ID {movie_id} not found in the database.")
        except PyMongoError as e:
            raise RuntimeError(f"Failed to delete movie due to a database error: {e}")

    def search_and_cache_movie(self, title: str) -> Optional[Movie]:
        # Search TMDb for the movie by title
        search_results = self.tmdb_movie.search(title)
        if not search_results:
            return None  # No results found

        # Select the top result
        top_result = search_results[0]
        movie_id = top_result.id

        # Check if the movie is already cached
        cached_movie = self.get_movie_by_id(movie_id)
        if cached_movie:
            return cached_movie

        # Fetch detailed movie information
        movie_data = self.tmdb_movie.details(movie_id)
        if not movie_data:
            return None

        # Create a Movie instance
        movie = Movie(
            id=movie_data.id,
            title=movie_data.title,
            overview=movie_data.overview,
            release_date=movie_data.release_date,
            poster_path=movie_data.poster_path,
        )

        # Cache the movie in MongoDB
        self.add_movie(movie)
        return movie

    def fetch_recommendations(self, title: str) -> Optional[List[Movie]]:
        # First fetch movie
        movie: Movie = self.search_and_cache_movie(title)

        # Fetch recommendations
        recommendataions = self.tmdb_movie.recommendations(movie.id)

        # Now lets cache the movies and create Movie objects
        return [self.search_and_cache_movie(rec.title()) for rec in recommendataions]
