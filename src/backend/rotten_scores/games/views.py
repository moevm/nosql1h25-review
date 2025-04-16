from django.shortcuts import render
from django.http import HttpResponse

def game_list(request):
    return HttpResponse("Заглушка лист игр")
def game_detail(request):
    return HttpResponse("Заглушка детали игры")
