from django.shortcuts import render
from django.http import HttpResponse, HttpResponseNotFound


def my_reviews_and_reviews(request):
    return render(request, 'profile/base_profile.html')


def load_section(request):
    section = request.GET.get('section', 'profile')

    # Маппинг названий разделов на файлы шаблонов
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