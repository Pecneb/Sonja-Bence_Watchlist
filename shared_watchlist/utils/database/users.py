from pydantic import BaseModel, EmailStr, HttpUrl
from typing import Optional, Dict, List
from abc import ABC, abstractmethod
from utils.database.db_config import db

"""
'userinfo': {
    'given_name': 'Bence', 
    'family_name': 'Péter', 
    'nickname': 'ecneb2000', 
    'name': 'Bence “Bence” Péter', 
    'picture': 'https://lh3.googleusercontent.com/a/ACg8ocLpWdRlPjwT3PCsel7nmIesjkojfc6uUv4FXfj8ys_W0bnDvplu=s96-c', 
    'updated_at': '2025-04-20T14:10:49.981Z', 
    'email': 'ecneb2000@gmail.com', 
    'email_verified': True, 
    'iss': 'https://dev-y02f2bpr8skxu785.us.auth0.com/', 
    'aud': 'cW7owP5Q52YHMZAnJwT8FPlH2ZKvvL3U', 
    'sub': 'google-oauth2|103384461793700128197', 
    'iat': 1745158250, 
    'exp': 1745194250, 
    'sid': 'tMK4-C-SpXAtMQKhw39LKYVSwjIJqOe8', 
    'nonce': 'fJarZRxoQqNtzA06TfPu'}
"""


class User(BaseModel):
    id: str
    given_name: str
    family_name: str
    nickname: str
    name: str
    email: EmailStr
    avatar_url: Optional[HttpUrl] = None

    def from_oauth_response(oauth_response: Dict):
        userinfo = oauth_response.get("userinfo", {})
        return User(
            id=userinfo.get("sub", ""),
            given_name=userinfo.get("given_name", ""),
            family_name=userinfo.get("family_name", ""),
            nickname=userinfo.get("nickname", ""),
            name=userinfo.get("name", ""),
            email=userinfo.get("email", ""),
            avatar_url=userinfo.get("picture"),
        )


class IUserRepository(ABC):
    @abstractmethod
    def search_user(self, text: str) -> User:
        pass

    @abstractmethod
    def get_user(self, user_id: str) -> User:
        pass

    @abstractmethod
    def add_user(self, user: User) -> None:
        pass

    @abstractmethod
    def remove_user(self, user_id: str) -> bool:
        pass

    @abstractmethod
    def add_friend(self, user_id: str, friend_id: str) -> None:
        pass

    @abstractmethod
    def remove_friend(self, user_id: str, friend_id: str):
        pass

    @abstractmethod
    def get_friends(self, user_id: str) -> List[User]:
        pass


class MongoUserRepository(IUserRepository):
    def __init__(self):
        self.collection = db["users"]

    def search_user(self, text: str):
        query = {
            "$or": [
                {"name": {"$regex": text, "$options": "i"}},
                {"given_name": {"$regex": text, "$options": "i"}},
                {"family_name": {"$regex": text, "$options": "i"}},
                {"nickname": {"$regex": text, "$options": "i"}},
                {"email": {"$regex": text, "$options": "i"}},
            ]
        }
        results = self.collection.find(query)
        return [User(**user_data) for user_data in results]

    def get_user(self, user_id: str) -> User:
        user_data = self.collection.find_one({"id": user_id})
        if not user_data:
            raise ValueError(f"User with id {user_id} not found")
        return User(**user_data)

    def add_user(self, user: User) -> None:
        if self.collection.find_one({"id": user.id}):
            raise ValueError(f"User with id {user.id} already exists")
        self.collection.insert_one(user.model_dump_json())

    def remove_user(self, user_id: str) -> bool:
        result = self.collection.delete_one({"id": user_id})
        return result.deleted_count > 0

    def add_friend(self, user_id: str, friend_id: str) -> None:
        self.collection.update_one(
            {"id": user_id}, {"$addToSet": {"friends": friend_id}}
        )

    def remove_friend(self, user_id: str, friend_id: str):
        self.collection.update_one({"id": user_id}, {"$pull": {"friends": friend_id}})

    def get_friends(self, user_id: str) -> List[User]:
        user_data = self.collection.find_one({"id": user_id})
        if not user_data or "friends" not in user_data:
            return []
        friend_ids = user_data["friends"]
        friends = self.collection.find({"id": {"$in": friend_ids}})
        return [User(**friend) for friend in friends]
