from typing import TypedDict
from datetime import datetime

from bson import ObjectId

from .review import UserReview, CriticReview


class StatsReviews(TypedDict):
    total: int
    avgRating: float


class Stats(TypedDict):
    userReviews: StatsReviews
    criticReviews: StatsReviews


class Game(TypedDict):
    _id: ObjectId
    title: str
    description: str
    developer: str
    publisher: str
    platforms: list[str]
    releaseDate: datetime

    stats: Stats
    recentUserReviews: list[UserReview]
    recentCriticReviews: list[CriticReview]

    lastModified: datetime
