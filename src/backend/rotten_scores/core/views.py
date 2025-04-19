from django.http import JsonResponse
from django.views.generic import TemplateView
from pymongo import MongoClient
from django.conf import settings
from datetime import datetime
from django.views.generic.edit import FormView
from django.contrib.auth import login, authenticate
from . import forms


class HomepageView(TemplateView):
    template_name = 'core/homepage.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Подключение к MongoDB
        client = MongoClient(settings.MONGODB_URI)
        db = client[settings.MONGODB_NAME]
        
        platform = self.request.GET.get('platform', 'PlayStation 5')
        
        # Получение новых релизов
        new_releases_pipeline = [
            {"$lookup": {
                "from": "critic_reviews",
                "localField": "_id",
                "foreignField": "game_id",
                "as": "critic_reviews"
            }},
            {"$project": {
                "_id": 1,
                "title": 1,
                "image_ref": "$imageUrl",
                "release_date": 1,
                "platforms": 1,
                "avg_rating": {"$avg": "$critic_reviews.rating"}
            }},
            {"$sort": {"release_date": -1}},
            {"$limit": 6}
        ]

        new_releases = list(db.games.aggregate(new_releases_pipeline))

        # Получение лучших игр на выбранной платформе
        best_platform_games_pipeline = [
            {"$match": {"platforms": {"$in": [platform]}}},
            {"$lookup": {
                "from": "critic_reviews",
                "localField": "_id",
                "foreignField": "game_id",
                "as": "critic_reviews"
            }},
            {"$project": {
                "_id": 1,
                "title": 1,
                "image_ref": "$imageUrl",
                "release_date": 1,
                "platforms": 1,
                "avg_rating": {"$avg": "$critic_reviews.rating"}
            }},
            {"$sort": {"avg_rating": -1}},
            {"$limit": 6}
        ]

        best_platform_games = list(db.games.aggregate(best_platform_games_pipeline))
        
        # Получение списка 5 популярных платформ
        all_platforms = ['PlayStation 5', 'PlayStation 4', 'Xbox One', 'Xbox','iOS']
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


        context.update({
            'new_releases': new_releases,
            'best_platform_games': best_platform_games,
            'current_platform': platform,
            'all_platforms': all_platforms,
            'page_title': 'GameScore - Агрегатор отзывов и оценок видеоигр',
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
