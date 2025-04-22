from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseNotFound
from pymongo import MongoClient
from django.conf import settings
from user_profile.forms import ChangePersonalDataForm, ChangePasswordForm


def my_ratings_and_reviews(request):
    client = MongoClient(settings.MONGO_DB_URI)
    db = client[settings.MONGO_DB_NAME]
    user_id = request.user.id

    data = [
          {
            "$match": {"userId": user_id }
          },
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
    }

    return render(request, 'profile/base_profile.html', context)


def custom_logout(request):
    if request.user.is_authenticated:
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
        'admin': 'admin.html'
    }

    template_name = f'profile/sections/{section_mapping.get(section, "ratings.html")}'

    try:
        return render(request, template_name)
    except:
        return HttpResponseNotFound("Section not found")


def account(request):
    personal_form = ChangePersonalDataForm(data=request.POST, user=request.user)
    password_form = ChangePasswordForm(data=request.POST, user=request.user)

    if request.method == 'POST':
        if 'form_type' in request.POST:
            form_type = request.POST['form_type']

            if form_type == 'personal' and personal_form.is_valid():
                personal_form.save()
                return custom_logout(request)

            elif form_type == 'password' and password_form.is_valid():
                password_form.save()
                return custom_logout(request)

    context = {
        'personal_form': personal_form,
        'password_form': password_form,
    }

    return render(request, 'profile/base_profile.html', context)


def statistics(request):
    user_id = request.user.id

    client = MongoClient(settings.MONGO_DB_URI)
    db = client[settings.MONGO_DB_NAME]

    user_reviews = list(db.user_reviews.find({"userId": user_id}))
    games_reviewed = len(user_reviews)

    if games_reviewed == 0:
        context = {
            'games_reviewed': 0,
            'favourite_platform': 'None',
            'favourite_genre': 'None',
        }
        return render(request, 'profile/base_profile.html', context)

    platform_counter = {}
    genre_counter = {}
    # TODO исправить получение платформы и жанра
    for review in user_reviews:
        platform = review.get("platform")
        if platform:
            platform_counter[platform] = platform_counter.get(platform, 0) + 1

        game = db.games.find_one({"_id": review["gameId"]})
        if game:
            for genre in game.get("genres", []):
                genre_counter[genre] = genre_counter.get(genre, 0) + 1

    favourite_platform = max(platform_counter, key=platform_counter.get, default='None')
    favourite_genre = max(genre_counter, key=genre_counter.get, default='None')

    context = {
        'games_reviewed': games_reviewed,
        'favourite_platform': favourite_platform,
        'favourite_genre': favourite_genre,
    }

    return render(request, 'profile/base_profile.html', context)


def admin_panel(request):
    return HttpResponse("Заглушка")