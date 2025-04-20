from django.shortcuts import render
from django.http import HttpResponse
from django.http import JsonResponse
from .models import Game
import logging
from pymongo import MongoClient
from django.conf import settings

def game_list(request):
    # return HttpResponse("Заглушка лист игр")
    query = request.GET.get('q', '')
    if query:
        games = Game.objects.filter(title__icontains=query)
    else:
        games = Game.objects.all()
    return render(request, 'game_list.html', {'games': games, 'query': query})

def game_detail(request):
    return HttpResponse("Заглушка детали игры")

logger = logging.getLogger(__name__)

def search_games(request):
    try:
        client = MongoClient(settings.MONGODB_URI)
        db = client[settings.MONGODB_NAME]

        query = request.GET.get('q', '').strip()
        logger.info(f"Search query: {query}")

        if 'games' not in db.list_collection_names():
            logger.error("Collection 'games' not found!")
            return JsonResponse([], safe=False)
        
        results = db.games.find(
            {"title": {"$regex": query, "$options": "i"}},
            {"title": 1, "cover_url": 1, "release_date": 1, "critic_score": 1}
        ).limit(5)

        games = []
        for game in results:
            game['id'] = str(game.pop('_id'))
            if 'release_date' in game:
                game['release_date'] = game['release_date'].strftime('%Y-%m-%d')
            games.append(game)

        return JsonResponse(games, safe=False)

    except Exception as e:
        print(f"Ошибка: {e}")
        return JsonResponse([], safe=False)