from typing import TypedDict, Literal
from enum import StrEnum
from datetime import datetime

from bson import ObjectId


class User(TypedDict):
    _id: ObjectId
    username: str
    hashed_password: str
    email: str
    role: Literal["user", "admin"]
    lastModified: datetime
