from django.shortcuts import render
from django.http import JsonResponse
from django.views.generic import TemplateView
from pymongo import MongoClient
from django.conf import settings
from datetime import datetime
from django.views.generic.edit import FormView
from django.contrib.auth import login
from django.urls import reverse_lazy
from . import forms
from . import models
from mongoengine.errors import DoesNotExist


class HomepageView(TemplateView):
    template_name = 'core/homepage.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Подключение к MongoDB
        client = MongoClient(settings.MONGODB_URI)
        db = client[settings.MONGODB_NAME]
        
        # Получаем выбранную платформу (по умолчанию PS5)
        platform = self.request.GET.get('platform', 'PS5')
        
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
                "image_ref": 1,
                "release_date": 1,
                "platforms": 1,
                "avg_rating": {"$avg": "$critic_reviews.rating"}
            }},
            {"$sort": {"release_date": -1}},
            {"$limit": 8}
        ]
        
        new_releases = list(db.games.aggregate(new_releases_pipeline))
        
        # Получение лучших игр на выбранной платформе
        best_platform_games_pipeline = [
            {"$match": {"platforms": {"$regex": platform, "$options": "i"}}},
            {"$lookup": {
                "from": "critic_reviews",
                "localField": "_id",
                "foreignField": "game_id",
                "as": "critic_reviews"
            }},
            {"$project": {
                "_id": 1,
                "title": 1,
                "image_ref": 1,
                "release_date": 1,
                "platforms": 1,
                "avg_rating": {"$avg": "$critic_reviews.rating"}
            }},
            {"$match": {"avg_rating": {"$gte": 85}}},  # Снижаем порог для получения большего числа игр
            {"$sort": {"avg_rating": -1}},
            {"$limit": 8}
        ]
        
        best_platform_games = list(db.games.aggregate(best_platform_games_pipeline))
        
        # Получение списка всех доступных платформ
        all_platforms = [
            "PS5", "PC", "Nintendo Switch", "PS4", "Xbox Series X", "Xbox One"
        ]
        
        # Форматирование дат и рейтингов
        for game in new_releases + best_platform_games:
            game['id'] = str(game['_id'])  # 💡 добавляем безопасный id для шаблона

            if 'release_date' in game and game['release_date']:
                if isinstance(game['release_date'], str):
                    try:
                        game['release_date'] = datetime.strptime(game['release_date'], '%Y-%m-%d')
                    except ValueError:
                        pass

            if 'avg_rating' in game and game['avg_rating']:
                game['avg_rating_display'] = round(game['avg_rating'])

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
    form_class = forms.EmailAuthenticationForm

    def form_valid(self, form):
        login(self.request, form.get_user())

        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'redirect_url': self.get_success_url(),
                'user': {
                    'is_authenticated': True,
                    'username': form.get_user().username
                }
            })
        return super().form_valid(form)

    def form_invalid(self, form):
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'error': form.errors.get('__all__', ['Неверный email или пароль'])[0]
            }, status=400)
        return super().form_invalid(form)