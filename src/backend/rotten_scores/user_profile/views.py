from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseNotFound
from pymongo.auth import logout


def my_reviews_and_reviews(request):
    return render(request, 'profile/base_profile.html')


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