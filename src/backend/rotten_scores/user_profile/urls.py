from django.urls import path
from . import views

urlpatterns = [
    path('', views.my_rating_and_reviews, name='my_reviews_and reviews'),
    path('account/', views.account, name='account'),
    path('statistics/', views.statistics_view, name='statistics'),
]