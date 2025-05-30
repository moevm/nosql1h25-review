from django.urls import path
from . import views

urlpatterns = [
    path('add/<str:game_id>/', views.add_review, name='add_review'),
    path('edit/<str:review_id>/', views.edit_review, name='edit_review'),
    path('delete/<str:review_id>/', views.delete_review, name='delete_review'),
    path('game/<str:game_id>/', views.ReviewListView.as_view(), name='review_list'),
]
