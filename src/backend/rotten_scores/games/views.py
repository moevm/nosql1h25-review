from django.views.generic import TemplateView
from django.http import HttpResponse
from pymongo import MongoClient
from django.conf import settings
from datetime import datetime
import sys
import os
from django.shortcuts import render, get_object_or_404
from bson.objectid import ObjectId

client = MongoClient(settings.MONGODB_URI)
db = client[settings.MONGODB_NAME]

# при открытии Games почему-то хэдер, футер и список троиться, поэтому пока заглушка
def game_list(request):
    return HttpResponse("Заглушка лист игр")
# def game_list(request):
#     games = list(db.games.find().limit(20))  # Можно добавить фильтры и пагинацию
    
#     for game in games:
#         game['id'] = str(game['_id'])

#         if 'releaseDate' in game and isinstance(game['releaseDate'], datetime):
#             game['release_date_formatted'] = game['releaseDate'].strftime('%Y-%m-%d')

#     return render(request, 'games/game_list.html', {'games': games})


def game_detail(request, pk):
    try:
        game = db.games.find_one({'_id': ObjectId(pk)})
    except Exception:
        game = None

    if not game:
        return render(request, '404.html', status=404)

    game['id'] = str(game['_id'])

    if 'releaseDate' in game and isinstance(game['releaseDate'], datetime):
        game['release_date_formatted'] = game['releaseDate'].strftime('%Y-%m-%d')

    return render(request, 'games/game_detail.html', {'game': game})
