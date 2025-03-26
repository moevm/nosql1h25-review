from typing import TypedDict, Literal
from enum import StrEnum
from datetime import datetime

from bson import ObjectId


class User(TypedDict):
    _id: ObjectId
    username: str
    hashedPassword: str
    email: str
    role: Literal["user", "admin"]

    createdAt: datetime
    lastModified: datetime
