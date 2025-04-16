from django.urls import path
from . import views

urlpatterns = [
    path('', views.my_reviews_and_reviews, name='my_reviews_and_reviews'),
    path('account/', views.account, name='account'),
    path('statistics/', views.statistics, name='statistics'),
]