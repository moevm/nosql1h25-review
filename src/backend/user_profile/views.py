import json
from datetime import datetime as py_datetime

from django.utils import timezone
from django.conf import settings
from django.utils.dateparse import parse_date
from django.contrib import messages
from django.shortcuts import render, redirect
from django.http import HttpResponseNotFound, HttpResponseForbidden, HttpResponse

from bson import datetime as bson_datetime, ObjectId

from pymongo import MongoClient

from src.backend.user_profile.forms import ChangePersonalDataForm, ChangePasswordForm
from src.utils.color_code import get_color_by_score

client = MongoClient(settings.MONGO_DB_URI)
db = client[settings.MONGO_DB_NAME]


def delete_game(request, game_id):
    if not request.user.is_staff:
        return HttpResponseForbidden("You don't have permission to delete games")

    try:
        obj_id = ObjectId(game_id)
    except:
        messages.error(request, "Invalid game ID format")
        return redirect('profile:admin_panel')

    game = db.games.find_one({"_id": obj_id})
    if not game:
        messages.error(request, "Game not found")
        return redirect('profile:admin_panel')


    db.user_reviews.delete_many({"gameId": obj_id})


    result = db.games.delete_one({"_id": obj_id})

    if result.deleted_count == 1:
        messages.success(request, "Game and all related reviews successfully deleted!")
    else:
        messages.error(request, "Failed to delete game")

    return redirect('profile:admin_panel')

def edit_game(request, game_id):
    if not request.user.is_staff:
        return HttpResponseForbidden("You don't have permission to edit games")

    try:
        game = db.games.find_one({"_id": ObjectId(game_id)})
    except:
        return HttpResponseNotFound("Invalid game ID")

    if not game:
        return HttpResponseNotFound("Game not found")


    game['id_str'] = str(game['_id'])


    context = {
        'section_template': 'profile/sections/edit_game.html',
        'game': game,
        'platforms_list': ['PS5', 'Xbox Series X/S', 'Nintendo Switch', 'PC', 'Mobile', 'PS4'],
        'genres_list': [
            'Action', 'Adventure', 'Role-playing (RPG)', 'Strategy', 'Simulation',
            'Sports', 'Racing', 'Fighting', 'Puzzle', 'Horror', 'Survival',
            'Battle Royale', 'MMORPG', 'MOBA', 'Platformer', 'Stealth', 'Sandbox',
            'Open World', 'First-person Shooter (FPS)', 'Third-person Shooter (TPS)',
            'Tactical Shooter', 'Roguelike', 'Metroidvania', 'Visual Novel', 'Rhythm',
            'Party', 'Educational', 'Card Game', 'Board Game', 'Trivia'
        ],
        'is_edit': True
    }
    if request.method == 'POST':
        title = request.POST.get('name')
        description = request.POST.get('description')
        released_on = request.POST.get('released_on')
        developer = request.POST.get('game_author')
        publisher = request.POST.get('game_author')
        image_url = request.POST.get('image_url')
        platforms = request.POST.getlist('platforms')
        genres = request.POST.getlist('genres')

        release_date = None
        if released_on:
            parsed_date = parse_date(released_on)
            if parsed_date:
                release_date = bson_datetime.datetime.combine(
                    parsed_date,
                    py_datetime.min.time()
                )

        update_data = {
            'title': title,
            'description': description,
            'developer': developer,
            'publisher': publisher,
            'platforms': platforms,
            'genres': genres,
            'imageUrl': image_url,
            'releaseDate': release_date,
            'lastModified': timezone.now()
        }

        try:
            db.games.update_one(
                {"_id": ObjectId(game_id)},
                {"$set": update_data}
            )
            messages.success(request, f"Game {title} successfully updated!")
            return redirect('profile:admin_panel')
        except Exception as e:
            messages.error(request, f"Error updating game: {e}")


    release_date = ""
    if game.get('releaseDate'):
        release_date = game['releaseDate'].strftime('%Y-%m-%d')

    context = {
        'section_template': 'profile/sections/edit_game.html',
        'game': game,
        'release_date': release_date,
        'is_edit': True
    }
    return render(request, 'profile/base_profile.html', context)
def my_ratings_and_reviews(request):
    user_id = request.user.id

    data = [
        {"$match": {"userId": ObjectId(user_id)}},
        {
            "$lookup": {
                "from": "games",
                "localField": "gameId",
                "foreignField": "_id",
                "as": "game_info"
            }
        },
        {
            "$project": {
                "_id": 1,
                "text": 1,
                "rating": 1,
                "createdAt": 1,
                "platform": 1,
                "game_info.title": 1,
                "game_info.imageUrl": 1
            }
        }
    ]

    reviews = list(db.user_reviews.aggregate(data))
    for review in reviews:
        review['color'] = get_color_by_score(float(review['rating'])).color
        review['review_id'] = str(review['_id'])

    context = {
        'reviews': reviews,
        'section_template': 'profile/sections/ratings.html',
    }

    return render(request, 'profile/base_profile.html', context)


def custom_logout(request):
    if request.user.is_authenticated:
        print(client.list_database_names())
        user = request.user
        user.logout()
        request.session.flush()
    return redirect('core:homepage')


def load_section(request):
    section = request.GET.get('section', 'profile')
    section_mapping = {
        'ratings': 'ratings.html',
        'account': 'account.html',
        'statistics': 'statistics.html',
        'admin_panel': 'admin.html'
    }
    template_name = f'profile/sections/{section_mapping.get(section, "ratings.html")}'
    try:
        return render(request, template_name)
    except:
        return HttpResponseNotFound("Section not found")


def account(request):
    personal_form = ChangePersonalDataForm(data=request.POST or None, user=request.user)
    password_form = ChangePasswordForm(data=request.POST or None, user=request.user)

    if request.method == 'POST':
        form_type = request.POST.get('form_type')

        if form_type == 'personal' and personal_form.is_valid():
            personal_form.save()
            return custom_logout(request)

        elif form_type == 'password' and password_form.is_valid():
            password_form.save()
            return custom_logout(request)

    context = {
        'personal_form': personal_form,
        'password_form': password_form,
        'section_template': 'profile/sections/account.html',
    }

    return render(request, 'profile/base_profile.html', context)


def statistics(request):
    user_id = request.user.id

    client = MongoClient(settings.MONGO_DB_URI)
    db = client[settings.MONGO_DB_NAME]

    user_reviews = list(db.user_reviews.find({"userId": user_id}))
    games_reviewed = len(user_reviews)

    platform_counter = {}
    genre_counter = {}

    for review in user_reviews:
        platform = review.get("platform")
        if platform:
            platform_counter[platform] = platform_counter.get(platform, 0) + 1

        game_id = review.get("gameId")
        if isinstance(game_id, str):
            from bson.objectid import ObjectId
            game_id = ObjectId(game_id)

        game = db.games.find_one({"_id": game_id})
        if game:
            genres = game.get("genres", [])
            for genre in genres:
                genre_counter[genre] = genre_counter.get(genre, 0) + 1

    favourite_platform = 'None'
    if platform_counter:
        favourite_platform = max(platform_counter.items(), key=lambda x: x[1])[0]

    favourite_genre = 'None'
    if genre_counter:
        favourite_genre = max(genre_counter.items(), key=lambda x: x[1])[0]

    context = {
        'games_reviewed': games_reviewed,
        'favourite_platform': favourite_platform,
        'favourite_genre': favourite_genre,
        'section_template': 'profile/sections/statistics.html',
    }

    return render(request, 'profile/base_profile.html', context)


def admin_panel(request):
    games_collection = db['games']

    if request.method == "POST" and request.FILES.get("json_file"):
        json_file = request.FILES["json_file"]
        data = json.load(json_file)

        for collection_name, documents in data.items():
            collection = db[collection_name]
            collection.drop()
            if documents:
                collection.insert_many(documents)

        redirect('core:homepage')

    if request.method == "POST" and request.POST.get("form_type") == "export":

        export_data = {}

        for collection_name in db.list_collection_names():
            collection = db[collection_name]
            export_data[collection_name] = list(collection.find({}, {'_id': False}))

        json_str = json.dumps(export_data, indent=2, default=str)
        response = HttpResponse(json_str, content_type="application/json")
        filename = f"rotten_scores_backup_{py_datetime.now().strftime('%d%m%Y')}.json"
        response["Content-Disposition"] = f'attachment; filename="{filename}"'
        return response

    if request.method == 'POST' and request.POST.get('form_type') == 'addgame':
        if not request.user.is_staff:  # Проверка на админа
            return HttpResponseForbidden("You don't have permission to add games")

        title = request.POST.get('name')
        description = request.POST.get('description')
        released_on = request.POST.get('released_on')
        developer = request.POST.get('game_author')
        publisher = request.POST.get('game_author')
        image_url = request.POST.get('image_url')
        platforms = request.POST.getlist('platforms')
        genres = request.POST.getlist('genres')

        release_date = None
        if released_on:
            parsed_date = parse_date(released_on)
            if parsed_date:
                release_date = bson_datetime.datetime.combine(
                    parsed_date,
                    py_datetime.min.time()
                )

        game = {
            'title': title,
            'description': description,
            'developer': developer,
            'publisher': publisher,
            'platforms': platforms,
            'genres': genres,
            'imageUrl': image_url,
            'releaseDate': release_date,
            'stats': {
                'userReviews': {'total': 0, 'avgRating': 0.0},
                'criticReviews': {'total': 0, 'avgRating': 0.0}
            },
            'lastModified': timezone.now()
        }

        try:
            result = games_collection.insert_one(game)
            messages.success(request, f"Game {title} successfully added!")
            return redirect('profile:admin_panel')
        except Exception as e:
            messages.error(request, f"Error saving game: {e}")

    all_games = list(games_collection.find().sort('lastModified', -1))
    # Преобразуем ObjectId в строку и сохраняем в новом поле без подчеркивания
    for game in all_games:
        game['id_str'] = str(game['_id'])  # Используем 'id_str' вместо '_id_str'

    context = {
        'section_template': 'profile/sections/admin.html',
        'games': all_games
    }
    return render(request, 'profile/base_profile.html', context)