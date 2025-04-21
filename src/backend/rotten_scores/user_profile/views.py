from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseNotFound
from pymongo import MongoClient
from django.conf import settings
from .models import GameReview
from datetime import datetime


def my_ratings_and_reviews(request):
    client = MongoClient(settings.MONGODB_URI)
    db = client[settings.MONGODB_NAME]
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

    print(reviews)

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
    return HttpResponse("Заглушка")
def statistics(request):
    return HttpResponse("Заглушка")
def admin_panel(request):
    return HttpResponse("Заглушка")