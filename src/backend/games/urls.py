from django.urls import path
from . import views

urlpatterns = [
    path('', views.GamesListView.as_view(), name='game_list'),
    path('search/', views.search_games, name='search_games'),
    path('<str:pk>/', views.game_detail, name='game_detail'),
]
