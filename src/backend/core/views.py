from django.views.generic import TemplateView
from django.shortcuts import render
from django.conf import settings
from datetime import datetime
from django.views.generic.edit import FormView
from django.contrib.auth import login, authenticate

from django.http import JsonResponse

from pymongo import MongoClient
from bson import json_util


from . import forms

from src.utils.color_code import get_color_by_score


class HomepageView(TemplateView):
    template_name = 'core/homepage.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Подключение к MongoDB
        client = MongoClient(settings.MONGO_DB_URI)
        db = client[settings.MONGO_DB_NAME]

        platform = self.request.GET.get('platform', 'PlayStation 5')

        # Получение новых релизов
        new_releases_pipeline = [
            {
        "$match": {
            "releaseDate": {"$lte": datetime.utcnow()}
        }
        },
            {"$project": {
                "_id": 1,
                "title": 1,
                "image_ref": "$imageUrl",
                "releaseDate": 1,
                "platforms": 1,
                "avg_rating": "$stats.criticReviews.avgRating"
            }},
            {"$sort": {"releaseDate": -1}},
            {"$limit": 6}
        ]

        new_releases = list(db.games.aggregate(new_releases_pipeline))

        # Получение лучших игр на выбранной платформе
        best_platform_games_pipeline = [
            {"$match": {"platforms": {"$in": [platform]}}},
            {"$project": {
                "_id": 1,
                "title": 1,
                "image_ref": "$imageUrl",
                "releaseDate": 1,
                "platforms": 1,
                "avg_rating": "$stats.criticReviews.avgRating"
            }},
            {"$sort": {"avg_rating": -1}},
            {"$limit": 6}
        ]

        best_platform_games = list(db.games.aggregate(best_platform_games_pipeline))

        # Получение списка 5 популярных платформ
        all_platforms = ['PlayStation 5', 'PlayStation 4', 'Xbox One', 'Xbox', 'iOS']
        # если хотим все платформы вывести
        # all_platforms = db.games.distinct("platforms")
        # all_platforms.sort()

        for game in new_releases + best_platform_games:
            game['id'] = str(game['_id'])

            if 'release_date' in game and game['release_date']:
                if isinstance(game['release_date'], str):
                    try:
                        game['release_date'] = datetime.strptime(game['release_date'], '%Y-%m-%d')
                    except ValueError:
                        pass

            if 'avg_rating' in game and game['avg_rating'] is not None:
                game['avg_rating_display'] = round(game['avg_rating'])
            else:
                game['avg_rating_display'] = 0

            if 'avg_rating' in game:
                color_code = get_color_by_score(game['avg_rating'])
                game['avg_rating_color'] = color_code.color
                game['avg_rating_message'] = color_code.message

        context.update({
            'new_releases': new_releases,
            'best_platform_games': best_platform_games,
            'current_platform': platform,
            'all_platforms': all_platforms,
        })

        return context


class LoginView(FormView):
    template_name = 'registration/login.html'
    form_class = forms.LoginForm

    def get_success_url(self):
        # Возвращаем URL, с которого пришел пользователь, или домашнюю страницу
        return self.request.POST.get('next', self.request.GET.get('next', '/'))

    def form_valid(self, form):
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password')

        user = authenticate(self.request, username=username, password=password)

        if user is None:
            return self.form_invalid(form)

        # TODO: заставить работать
        login(self.request, user)  # Функция для сохранения сессии (для записи в куках)

        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'redirect_url': self.get_success_url(),
                'user': {
                    'is_authenticated': True,
                    'username': username
                }
            })
        return super().form_valid(form)

    def form_invalid(self, form):
        print(form.errors)
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'error': form.errors.get('__all__', ['Неверный username или пароль'])[0]
            }, status=400)
        return super().form_invalid(form)


def database_view(request):
    client = MongoClient(settings.MONGO_DB_URI)
    db = client[settings.MONGO_DB_NAME]

    collection_names = [name for name in db.list_collection_names() if not name.startswith('system.')]

    all_data = {}
    for collection_name in collection_names:
        collection = db[collection_name]
        documents = list(collection.find({}))

        all_data[collection_name] = documents

    client.close()
    return render(request, "profile/db_viewer.html", {"json_str": json_util.dumps(all_data)})
