from django.shortcuts import render, redirect
from django.http import HttpResponseNotFound, HttpResponseForbidden
from django.utils import timezone
from django.conf import settings
from django.utils.dateparse import parse_date
from django.contrib import messages

from bson import datetime as bson_datetime, ObjectId
from datetime import datetime as py_datetime

from pymongo import MongoClient

from user_profile.forms import ChangePersonalDataForm, ChangePasswordForm

from utils.color_code import get_color_by_score

client = MongoClient(settings.MONGO_DB_URI)
db = client[settings.MONGO_DB_NAME]


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
            'createdAt': timezone.now(),
            'lastModified': timezone.now()
        }

        try:
            result = games_collection.insert_one(game)
            messages.success(request, f"Game {title} successfully added!")
            return redirect('profile:admin_panel')
        except Exception as e:
            messages.error(request, f"Error saving game: {e}")

    all_games = list(games_collection.find().sort('lastModified', -1))

    context = {
        'section_template': 'profile/sections/admin.html',
        'games': all_games
    }
    return render(request, 'profile/base_profile.html', context)