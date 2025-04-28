from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseNotFound
from django.template.defaulttags import now
from django.utils import timezone
from django.utils.datetime_safe import datetime
from djongo.database import Binary
from pymongo import MongoClient
from django.conf import settings
from user_profile.forms import ChangePersonalDataForm, ChangePasswordForm

client = MongoClient("mongodb://localhost:27017/")
db = client['game_reviews_db']
games_collection = db['games']


def my_ratings_and_reviews(request):
    user_id = request.user.id

    data = [
        {"$match": {"userId": user_id}},
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
                "_id": 0,
                "text": 1,
                "rating": 1,
                "createdAt": 1,
                "game_info.title": 1,
                "game_info.imageUrl": 1
            }
        }
    ]

    reviews = list(db.user_reviews.aggregate(data))

    context = {
        'reviews': reviews,
        'section_template': 'profile/sections/ratings.html',
    }

    return render(request, 'profile/base_profile.html', context)


def account_view(request):
    if request.method == 'POST':
        form_type = request.POST.get('form_type')

        if form_type == 'addgame':
            name = request.POST.get('name')
            description = request.POST.get('description')
            released_on = request.POST.get('released_on')
            game_author = request.POST.get('game_author')

            platforms = request.POST.getlist('platforms')
            genres = request.POST.getlist('genres')

            # Сохраняем картинку
            image_file = request.FILES.get('game_image')
            image_path = None
            if image_file:
                # например, сохраняем локально
                with open(f'media/games/{image_file.name}', 'wb+') as destination:
                    for chunk in image_file.chunks():
                        destination.write(chunk)
                image_path = f'media/games/{image_file.name}'

            game = {
                'name': name,
                'description': description,
                'released_on': released_on,
                'game_author': game_author,
                'platforms': platforms,
                'genres': genres,
                'image_path': image_path,
                'created_at': timezone.now(),
                'updated_at': timezone.now(),
            }

            games_collection.insert_one(game)

            return redirect('account')  # редиректим обратно на аккаунт после сохранения

    return render(request, 'account.html')

def custom_logout(request):
    if request.user.is_authenticated:
        print(client.list_database_names())
        # Получаем текущего пользователя и вызываем его метод logout
        user = request.user
        user.logout()

        # Очищаем сессию
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
    context = {
        'section_template': 'profile/sections/admin.html',
    }
    return render(request, 'profile/base_profile.html', context)
