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
    return HttpResponse("Заглушка")

def admin_panel(request):
    return HttpResponse("Заглушка")