from src.schemas import CriticReview, UserReview, Game

from typing import Any

from datetime import datetime

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden, HttpResponse, HttpRequest
from django.contrib import messages
from django.conf import settings
from django.views import View

from pymongo import MongoClient
from pymongo.collection import Collection

from bson import ObjectId

client = MongoClient(settings.MONGO_DB_URI)
db = client[settings.MONGO_DB_NAME]


class ReviewListView(View):
    template_name = "reviews/review_list.html"
    score_filters = {
        "user": {
            "all": {},
            "positive": {"$gte": 8},
            "mixed": {"$gte": 5, "$lt": 8},
            "negative": {"$lt": 5},
        },
        "critic": {
            "all": {},
            "positive": {"$gte": 80},
            "mixed": {"$gte": 50, "$lt": 80},
            "negative": {"$lt": 50},
        }
    }

    def get(self, request: HttpRequest, game_id: str) -> HttpResponse:
        filters = self._parse_filters(request)

        reviews_collection = self._get_collection(filters['review_type'])

        game = self._find_game(game_id)
        reviews = self._find_reviews(reviews_collection, game_id, filters)

        context = self._build_context(game, reviews, filters)

        return render(request, self.template_name, context)

    @staticmethod
    def _parse_filters(request: HttpRequest) -> dict[str, Any]:
        return {
            "platform": request.GET.get("platform"),
            "sort_by": request.GET.get("sort", "rating"),
            "score_type": request.GET.get("score_type", "all"),
            "review_type": request.GET.get("review_type", "critic"),
            "order": request.GET.get("order", "desc"),
        }

    @staticmethod
    def _get_collection(review_type: str) -> Collection:
        if review_type == "critic":
            return db["critic_reviews"]
        elif review_type == "user":
            return db["user_reviews"]
        raise ValueError("Invalid review type")

    @staticmethod
    def _find_game(game_id: str) -> Game:
        game = db.games.find_one({"_id": ObjectId(game_id)})
        if not game:
            raise ValueError("Game not found")
        return game

    def _find_reviews(self, reviews_collection: Collection,
                      game_id: str, filters: dict[str, Any]
                      ) -> list[CriticReview | UserReview]:
        query = {"gameId": ObjectId(game_id)}
        if filters["platform"]:
            query["platform"] = filters["platform"]
        if filters["score_type"] != "all":
            score_filter = self._score_type_to_filter(
                filters["score_type"], filters["review_type"]
            )
            query["rating"] = score_filter
        sort_order = 1 if filters["order"] == "asc" else -1
        return list(reviews_collection
                    .find(query)
                    .sort(filters["sort_by"], sort_order))

    @staticmethod
    def _score_type_to_filter(score_type: str, review_type: str) -> dict[str, Any]:
        if (review_type not in ReviewListView.score_filters
                or score_type not in ReviewListView.score_filters[review_type]):
            raise ValueError("Invalid score type or review type")
        return ReviewListView.score_filters[review_type][score_type]

    @staticmethod
    def _build_context(game: Game, reviews: list[CriticReview | UserReview], filters: dict[str, Any]) -> dict[str, Any]:
        return {
            "game": game,
            "reviews": reviews,
            "platform": filters["platform"],
            "sort_by": filters["sort_by"],
            "score_type": filters["score_type"],
            "review_type": filters["review_type"],
            "order": filters["order"],
        }


@login_required
def add_review(request, game_id):
    if request.method == 'POST':
        user = request.user
        game = db.games.find_one({'_id': ObjectId(game_id)})

        if not game:
            return render(request, '404.html', status=404)

        text = request.POST.get('text')
        rating = int(request.POST.get('rating'))
        platform = request.POST.get('platform')

        existing_review = db.user_reviews.find_one({
            'gameId': ObjectId(game_id),
            'userId': ObjectId(user.id),
            'platform': platform
        })

        if existing_review:
            return HttpResponseForbidden('You have already reviewed this game on this platform.')

        review = {
            'gameId': ObjectId(game_id),
            'userId': ObjectId(user.id),
            'gameTitle': game.get('title'),
            'text': text,
            'rating': rating,
            'platform': platform,
            'createdAt': datetime.now(),
            'lastModified': datetime.now()
        }
        db.user_reviews.insert_one(review)
        db.games.update_one(
            {'_id': ObjectId(game_id)},
            {'$push': {
                'recentUserReviews': {
                    '$each': [review],
                    '$position': 0
                }
            }}
        )
        return redirect('games:game_detail', pk=game_id)

    return redirect('games:game_detail', pk=game_id)


@login_required
def edit_review(request, review_id):
    try:
        review = db.user_reviews.find_one({'_id': ObjectId(review_id)})

        if not review:
            return render(request, '404.html', status=404)

        if review['userId'] != ObjectId(request.user.id):
            return HttpResponseForbidden('У вас нет прав для редактирования этого отзыва.')

        game = db.games.find_one({'_id': review['gameId']})

        if request.method == 'POST':
            text = request.POST.get('text')
            rating = int(request.POST.get('rating'))
            platform = request.POST.get('platform')

            db.user_reviews.update_one(
                {'_id': ObjectId(review_id)},
                {
                    '$set': {
                        'text': text,
                        'rating': rating,
                        'platform': platform,
                        'lastModified': datetime.utcnow()
                    }
                }
            )

            messages.success(request, 'Отзыв успешно обновлен.')
            return redirect('profile:my_rating_and_reviews')
        user_reviews = db.user_reviews.find({
            'gameId': review['gameId'],
            'userId': ObjectId(request.user.id),
            '_id': {'$ne': ObjectId(review_id)}
        })
        used_platforms = {r['platform'] for r in user_reviews}

        all_platforms = game.get('platforms', [])
        available_platforms = [p for p in all_platforms if p not in used_platforms or p == review['platform']]

        return render(request, 'reviews/edit_review.html', {
            'review': review,
            'game': game,
            'available_platforms': available_platforms,
            'rating_choices': range(1, 11),
        })

    except Exception as e:
        messages.error(request, f'Произошла ошибка при редактировании отзыва: {str(e)}')
        return redirect('profile:my_rating_and_reviews')


@login_required
def delete_review(request, review_id):
    try:
        review = db.user_reviews.find_one({'_id': ObjectId(review_id)})

        if not review:
            return render(request, '404.html', status=404)

        if review['userId'] != ObjectId(request.user.id):
            return HttpResponseForbidden('У вас нет прав для удаления этого отзыва.')

        if request.method == 'POST':
            db.user_reviews.delete_one({'_id': ObjectId(review_id)})
            messages.success(request, 'Отзыв успешно удален.')
            return redirect('profile:my_rating_and_reviews')

        game_info = db.games.find_one({'_id': review['gameId']})
        return render(request, 'reviews/confirm_delete.html', {
            'review': review,
            'game': game_info
        })

    except Exception as e:
        messages.error(request, f'Произошла ошибка при удалении отзыва: {str(e)}')
        return redirect('profile:my_rating_and_reviews')
