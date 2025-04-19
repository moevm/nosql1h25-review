from pymongo import MongoClient
from fastapi import APIRouter, Query
from typing import List

router = APIRouter()

client = MongoClient("mongodb://localhost:27017/")
database = client["rotten_scores"]
games = database["games"]


@router.get("/search")
def search_games(query: str = Query(..., min_length=1)) -> List[str]:
    search_filter = {
        "title": {
            "$regex": f"^{query}",
            "$options": "i" #ignore register
        }
    }
    projection = {
        "title": 1,   # только название
        "_id": 0
    }

    #запрос
    cursor = games.find(search_filter, projection)
    limited_cursor = cursor.limit(10)
    results = list(limited_cursor)

    titles = [item["title"] for item in results]

    return titles
