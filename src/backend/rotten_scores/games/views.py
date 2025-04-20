from django.shortcuts import render
from django.http import HttpResponse
from django.http import JsonResponse
from .models import Game
import logging
from pymongo import MongoClient
from django.conf import settings
from datetime import datetime

def game_list(request):
    # return HttpResponse("Заглушка лист игр")
    query = request.GET.get('q', '')
    if query:
        games = Game.objects.filter(title__icontains=query)
    else:
        games = Game.objects.all()
    return render(request, 'game_list.html', {'games': games, 'query': query})

def game_detail(request, pk):
    return HttpResponse("Заглушка детали игры")

logger = logging.getLogger(__name__)


def search_games(request):
    try:
        client = MongoClient(settings.MONGODB_URI)
        db = client[settings.MONGODB_NAME]
        query = request.GET.get('q', '').strip().lower()

        if not query or 'games' not in db.list_collection_names():
            return JsonResponse([], safe=False)

        query_words = query.split()
        first_word = query_words[0]

        # 1. Точное совпадение начала названия (с учетом регистра)
        exact_start = list(db.games.find(
            {"title": {"$regex": f"^{query}", "$options": "i"}},
            {"title": 1, "imageUrl": 1, "releaseDate": 1, "stats": 1, "genres": 1}
        ).limit(5))

        # 2. Начинается с первого слова запроса
        starts_with_first_word = list(db.games.find(
            {"title": {"$regex": f"^{first_word}", "$options": "i"}},
            {"title": 1, "imageUrl": 1, "releaseDate": 1, "stats": 1, "genres": 1}
        ).limit(5))

        # 3. Все слова запроса присутствуют в любом порядке
        all_words_query = {"$and": [{"title": {"$regex": f"{word}", "$options": "i"}} for word in query_words]}
        contains_all_words = list(db.games.find(
            all_words_query,
            {"title": 1, "imageUrl": 1, "releaseDate": 1, "stats": 1, "genres": 1}
        ).limit(5))

        # 4. Любое частичное совпадение
        partial_match = list(db.games.find(
            {"title": {"$regex": query, "$options": "i"}},
            {"title": 1, "imageUrl": 1, "releaseDate": 1, "stats": 1, "genres": 1}
        ).limit(5))

        # Объединяем результаты, устраняя дубликаты
        seen_ids = set()
        results = []

        for group in [exact_start, starts_with_first_word, contains_all_words, partial_match]:
            for game in group:
                game_id = str(game['_id'])
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
            'January', 'February', 'March', 'April', 'May', 'June',
            'July', 'August', 'September', 'October', 'November', 'December'
        ]

        for game in results:
            # Форматирование даты
            release_date = game.get('releaseDate')
            formatted_date = 'N/A'

            if release_date:
                try:
                    if isinstance(release_date, str):
                        # Пробуем разные форматы даты
                        try:
                            release_date = datetime.strptime(release_date, '%Y-%m-%d')
                        except ValueError:
                            try:
                                release_date = datetime.strptime(release_date, '%m/%d/%Y')
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
                    formatted_date = 'N/A'

            game_data = {
                'id': str(game['_id']),
                'title': game.get('title', ''),
                'imageUrl': game.get('imageUrl', ''),
                'releaseDate': formatted_date,  # Используем отформатированную дату
                'criticRating': game.get('stats', {}).get('criticReviews', {}).get('avgRating', 'N/A'),
                'genres': ', '.join(game.get('genres', [])),
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

        games.sort(key=lambda x: (relevance_score(x['title']), x['title']))

        return JsonResponse(games[:5], safe=False)

    except Exception as e:
        logger.error(f"Search error: {str(e)}")
        return JsonResponse([], safe=False)