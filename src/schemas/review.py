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
    timestamp: datetime
    platform: str


class CriticReview(TypedDict):
    _id: ObjectId
    gameId: ObjectId
    publication: str
    gameTitle: str
    rating: int
    text: str
    fullReviewLink: str
    timestamp: datetime
    platforms: list[str]
