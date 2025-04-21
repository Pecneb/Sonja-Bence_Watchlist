import solara
from solara import Reactive
from utils.database.users import User
from typing import cast

user: Reactive[User] = solara.reactive(cast(None, User))