from src.utils.color_code import get_color_by_score
from src.schemas import Game

import logging
from datetime import datetime
from typing import Any

from django.http import HttpResponse, JsonResponse, HttpRequest
from django.core.paginator import Paginator, Page, EmptyPage, PageNotAnInteger
from django.views import View
from django.conf import settings
from django.shortcuts import render

from pymongo import MongoClient, ASCENDING, DESCENDING
from pymongo.collection import Collection

from bson.objectid import ObjectId

logger = logging.getLogger(__name__)

client = MongoClient(settings.MONGO_DB_URI)
db = client[settings.MONGO_DB_NAME]


class GamesListView(View):
    template_name: str = "games/game_list.html"
    games_per_page: int = 18

    def get(self, request: HttpRequest) -> HttpResponse:
        filters = self._parse_filters(request)
        query = self._build_query(filters)
        sort_field, sort_order = self._get_sorting(filters)

        collection: Collection[Game] = db["games"]
        games = list(collection.find(query).sort(sort_field, sort_order))

        page_obj = self._get_page(request, games)

        all_platforms = self._sort_platforms_by_appearance()
        all_genres = sorted(collection.distinct("genres"))

        context = self._build_context(
            total_games=len(games),
            filters=filters,
            all_platforms=all_platforms,
            all_genres=all_genres,
            page_obj=page_obj,
            is_paginated=page_obj.has_other_pages(),
        )
        return render(request, self.template_name, context)

    @staticmethod
    def _parse_filters(request: HttpRequest) -> dict[str, Any]:
        return {
            "platforms": request.GET.getlist("platform"),
            "genres": request.GET.getlist("genre"),
            "sort_by": request.GET.get("sort", "releaseDate"),
            "order": request.GET.get("order", "desc"),
        }

    @staticmethod
    def _build_query(filters: dict[str, Any]) -> dict[str, Any]:
        query: dict[str, Any] = {}
        if filters["platforms"]:
            query["platforms"] = {"$in": filters["platforms"]}
        if filters["genres"]:
            query["genres"] = {"$in": filters["genres"]}
        return query

    @staticmethod
    def _get_sorting(filters: dict[str, Any]) -> tuple[str, int]:
        sort_map: dict[str, str] = {
            "releaseDate": "releaseDate",
            "user_score": "stats.userReviews.avgRating",
            "critic_score": "stats.criticReviews.avgRating",
        }
        sort_field: str = sort_map.get(filters["sort_by"], "releaseDate")
        sort_order: int = DESCENDING if filters["order"] == "desc" else ASCENDING

        return sort_field, sort_order

    @staticmethod
    def _get_page(request: HttpRequest, games: list[Game]) -> Page:
        page_number = request.GET.get("page", "1")
        per_page = int(request.GET.get("per_page", GamesListView.games_per_page))

        paginator = Paginator(games, per_page)
        try:
            page_obj = paginator.page(page_number)
        except PageNotAnInteger:
            page_obj = paginator.page(1)
        except EmptyPage:
            page_obj = paginator.page(paginator.num_pages)
        return page_obj

    @staticmethod
    def _sort_platforms_by_appearance() -> list[str]:
        platform_counts = db["games"].aggregate(
            [
                {"$unwind": "$platforms"},
                {"$group": {"_id": "$platforms", "count": {"$sum": 1}}},
                {"$sort": {"count": -1}},
            ]
        )
        return [p["_id"] for p in platform_counts]

    @staticmethod
    def _build_context(
        total_games: int,
        filters: dict[str, Any],
        all_platforms: list[str],
        all_genres: list[str],
        page_obj: Page,
        is_paginated: bool,
    ) -> dict[str, Any]:
        return {
            "games": page_obj.object_list,
            "total_games": total_games,
            "platforms": all_platforms,
            "genres": all_genres,
            "selected_platforms": filters["platforms"],
            "selected_genres": filters["genres"],
            "sort_by": filters["sort_by"],
            "order": filters["order"],
            "page_obj": page_obj,
            "is_paginated": is_paginated,
        }


def game_detail(request, pk):
    try:
        game = db.games.find_one({"_id": ObjectId(pk)})
    except Exception:
        game = None

    if not game:
        return render(request, "404.html", status=404)

    critic_reviews = []
    user_reviews = []

    game["id"] = str(game["_id"])

    if "recentCriticReviews" in game:
        critic_reviews = game["recentCriticReviews"]
        for review in critic_reviews:
            score = review["rating"]
            review["score_color"] = get_color_by_score(score, "critic").color

    if "recentUserReviews" in game:
        user_reviews = game["recentUserReviews"]
        for review in user_reviews:
            user = db.users.find_one({"_id": review["userId"]})
            review["username"] = user["username"]
            review["score_color"] = get_color_by_score(review["rating"], "user").color
            # Добавляем platform, если его нет
            review["platform"] = review.get("platform", "Unknown")
            # Преобразуем дату в строку, если нужно
            if isinstance(review.get("createdAt"), datetime):
                review["createdAt"] = review["createdAt"].strftime("%b %d, %Y")

    can_review = False
    available_platforms = []

    is_released = True
    if "releaseDate" in game and isinstance(game["releaseDate"], datetime):
        game["release_date_formatted"] = game["releaseDate"].strftime("%b %d, %Y")
        is_released = game["releaseDate"] <= datetime.now()

    if request.user.is_authenticated:
        cursor = db.user_reviews.find(
            {"gameId": ObjectId(pk), "userId": ObjectId(request.user.id)}
        )
        user_reviews_by_current_user = list(cursor)
        reviewed_platforms = {
            review["platform"] for review in user_reviews_by_current_user
        }
        available_platforms = [
            p for p in game.get("platforms", []) if p not in reviewed_platforms
        ]
    else:
        available_platforms = game.get("platforms", [])

    average_score = 0
    average_score_color = None
    average_score_message = None
    if "stats" in game and "criticReviews" in game["stats"]:
        average_score = game["stats"]["criticReviews"]["avgRating"]
        average_score_color = get_color_by_score(average_score, "critic").color
        average_score_message = get_color_by_score(average_score, "critic").message

    context = {
        "game": game,
        "critic_reviews": critic_reviews,
        "user_reviews": user_reviews,
        "range_1_10": range(1, 11),
        "is_released": is_released,
        "available_platforms": available_platforms,
        "average_score": average_score,
        "average_score_color": average_score_color,
        "average_score_message": average_score_message,
    }

    return render(request, "games/game_detail.html", context)


def search_games(request):
    try:
        query = request.GET.get("q", "").strip().lower()

        if not query or "games" not in db.list_collection_names():
            return JsonResponse([], safe=False)

        query_words = query.split()
        first_word = query_words[0]

        # 1. Точное совпадение начала названия (с учетом регистра)
        exact_start = list(
            db.games.find(
                {"title": {"$regex": f"^{query}", "$options": "i"}},
                {"title": 1, "imageUrl": 1, "releaseDate": 1, "stats": 1, "genres": 1},
            ).limit(5)
        )

        # 2. Начинается с первого слова запроса
        starts_with_first_word = list(
            db.games.find(
                {"title": {"$regex": f"^{first_word}", "$options": "i"}},
                {"title": 1, "imageUrl": 1, "releaseDate": 1, "stats": 1, "genres": 1},
            ).limit(5)
        )

        # 3. Все слова запроса присутствуют в любом порядке
        all_words_query = {
            "$and": [
                {"title": {"$regex": f"{word}", "$options": "i"}}
                for word in query_words
            ]
        }
        contains_all_words = list(
            db.games.find(
                all_words_query,
                {"title": 1, "imageUrl": 1, "releaseDate": 1, "stats": 1, "genres": 1},
            ).limit(5)
        )

        # 4. Любое частичное совпадение
        partial_match = list(
            db.games.find(
                {"title": {"$regex": query, "$options": "i"}},
                {"title": 1, "imageUrl": 1, "releaseDate": 1, "stats": 1, "genres": 1},
            ).limit(5)
        )

        # Объединяем результаты, устраняя дубликаты
        seen_ids = set()
        results = []

        for group in [
            exact_start,
            starts_with_first_word,
            contains_all_words,
            partial_match,
        ]:
            for game in group:
                game_id = str(game["_id"])
                if game_id not in seen_ids and len(results) < 5:
                    seen_ids.add(game_id)
                    results.append(game)
                if len(results) >= 5:
                    break
            if len(results) >= 5:
                break

        # Форматируем результаты
        games = []
        month_names = [
            "January",
            "February",
            "March",
            "April",
            "May",
            "June",
            "July",
            "August",
            "September",
            "October",
            "November",
            "December",
        ]

        for game in results:
            # Форматирование даты
            release_date = game.get("releaseDate")
            formatted_date = "N/A"

            if release_date:
                try:
                    if isinstance(release_date, str):
                        # Пробуем разные форматы даты
                        try:
                            release_date = datetime.strptime(release_date, "%Y-%m-%d")
                        except ValueError:
                            try:
                                release_date = datetime.strptime(
                                    release_date, "%m/%d/%Y"
                                )
                            except ValueError:
                                release_date = None

                    if release_date:
                        # Форматируем в нужный формат (23 May 2015)
                        day = release_date.day
                        month = month_names[release_date.month - 1]
                        year = release_date.year
                        formatted_date = f"{day} {month} {year}"

                except Exception as e:
                    logger.error(f"Error formatting date: {str(e)}")
                    formatted_date = "N/A"

            critic_rating = (
                game.get("stats", {}).get("criticReviews", {}).get("avgRating", "N/A")
            )
            color = (
                get_color_by_score(critic_rating).color
                if critic_rating != "N/A"
                else None
            )
            game_data = {
                "id": str(game["_id"]),
                "title": game.get("title", ""),
                "imageUrl": game.get("imageUrl", ""),
                "releaseDate": formatted_date,
                "criticRating": critic_rating,
                "genres": ", ".join(game.get("genres", [])),
                "color": color,
            }
            games.append(game_data)

        # Сортируем по релевантности
        def relevance_score(title):
            title_lower = title.lower()
            if title_lower.startswith(query):
                return 0
            elif title_lower.startswith(first_word):
                return 1
            elif all(word in title_lower for word in query_words):
                return 2
            else:
                return 3

        games.sort(key=lambda x: (relevance_score(x["title"]), x["title"]))

        return JsonResponse(games[:5], safe=False)

    except Exception as e:
        logger.error(f"Search error: {str(e)}")
        return JsonResponse([], safe=False)
