from pymongo import MongoClient
from bson.objectid import ObjectId
from abc import ABC, abstractmethod
from typing import List
from db_config import db
from pydantic import BaseModel
from movies import Movie


# Initialize MongoDB client
# client = MongoClient("mongodb://localhost:27017/")
# db = client["watchlist_db"]  # Replace with your database name
# watchlist_collection = db["watchlists"]  # Replace with your collection name


class WatchlistItem(BaseModel):
    movie_id: int
    watched: bool


class Watchlist(BaseModel):
    id: str
    name: str
    owner_id: str
    collaborators: List[str]
    items: List[WatchlistItem]


class IWatchlistItemRepository(ABC):
    @abstractmethod
    def add_item(self, watchlist_id: str, item: WatchlistItem) -> None:
        pass

    @abstractmethod
    def remove_item(self, watchlist_id: str, movie_id: int) -> None:
        pass

    @abstractmethod
    def mark_as_watched(self, watchlist_id: str, movie_id: int) -> None:
        pass

    @abstractmethod
    def get_item(self, watchlist_id: str, movie_id: int) -> WatchlistItem:
        pass


class IWatchlistRepository(ABC):
    @abstractmethod
    def get_all(self, user_id: str) -> List[Watchlist]:
        pass

    @abstractmethod
    def get_watchlist_by_id(self, watchlist_id: int) -> Watchlist:
        pass

    @abstractmethod
    def create_watchlist(self, user_id: str, watchlist: Watchlist) -> None:
        pass

    @abstractmethod
    def remove_watchlist(self, user_id: str, item_id: str) -> None:
        pass

    @abstractmethod
    def add_collaborator(
        self, watchlist_id: int, collaborator_id: str, persmission: str
    ) -> None:
        pass


class MongoWatchlistRepository(IWatchlistRepository):
    def __init__(self):
        self.collection = db["watchlist"]

    def get_all(self, user_id: str) -> List[Watchlist]:
        watchlists = self.collection.find({"owner_id": user_id})
        return [Watchlist(**watchlist) for watchlist in watchlists]

    def get_watchlist_by_id(self, watchlist_id: int) -> Watchlist:
        watchlist = self.collection.find_one({"_id": ObjectId(watchlist_id)})
        if not watchlist:
            raise ValueError("Watchlist not found")
        return Watchlist(**watchlist)

    def create_watchlist(self, user_id: str, watchlist: Watchlist) -> None:
        watchlist_data = watchlist.dict()
        watchlist_data["owner_id"] = user_id
        self.collection.insert_one(watchlist_data)

    def remove_watchlist(self, user_id: str, item_id: str) -> None:
        result = self.collection.delete_one(
            {"_id": ObjectId(item_id), "owner_id": user_id}
        )
        if result.deleted_count == 0:
            raise ValueError("Watchlist not found or not authorized to delete")

    def add_collaborator(
        self, watchlist_id: int, collaborator_id: str, permission: str
    ) -> None:
        result = self.collection.update_one(
            {"_id": ObjectId(watchlist_id)},
            {"$addToSet": {"collaborators": collaborator_id}},
        )
        if result.matched_count == 0:
            raise ValueError("Watchlist not found")

    def add_item(self, watchlist_id: int, movie_id: int) -> None:
        result = self.collection.update_one(
            {"_id": ObjectId(watchlist_id)}, {"$addToSet": {"movies": movie_id}}
        )
        if result.matched_count == 0:
            raise ValueError("Watchlist not found")
