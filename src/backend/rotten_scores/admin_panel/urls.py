from django.urls import path
from . import views

urlpatterns = [
    path('', views.admin_dashboard, name='admin_dashboard'),
    path('games/', views.admin_game_list, name='admin_game_list'),
    path('games/add/', views.add_game, name='add_game'),
    path('games/<int:pk>/edit/', views.edit_game, name='edit_game'),
    path('games/<int:pk>/delete/', views.delete_game, name='delete_game'),
    path('import-export/', views.import_export, name='import_export'),
]
