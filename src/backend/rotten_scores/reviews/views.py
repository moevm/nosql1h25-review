from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden, HttpResponse
from django.conf import settings

from bson import ObjectId
from pymongo import MongoClient
from datetime import datetime

client = MongoClient(settings.MONGO_DB_URI)
db = client[settings.MONGO_DB_NAME]


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
        return redirect('games:game_detail', pk=game_id)

    return redirect('games:game_detail', pk=game_id)


def edit_review(request):
    return HttpResponse("Заглушка")


def delete_review(request):
    return HttpResponse("Заглушка")


def review_list(request):
    return HttpResponse("Заглушка")
