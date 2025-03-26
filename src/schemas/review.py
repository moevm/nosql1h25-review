from typing import TypedDict
from datetime import datetime

from bson import ObjectId


class UserReview(TypedDict):
    _id: ObjectId
    gameId: ObjectId
    userId: ObjectId

    gameTitle: str
    rating: int
    text: str
    platform: str

    createdAt: datetime
    lastModified: datetime


class CriticReview(TypedDict):
    _id: ObjectId
    gameId: ObjectId

    publication: str
    gameTitle: str
    rating: int
    text: str
    fullReviewLink: str
    platforms: list[str]

    createdAt: datetime
