from django.contrib.auth.views import LogoutView
from django.shortcuts import redirect
from django.urls import path
from . import views

app_name = 'profile'


urlpatterns = [
    path('', lambda request: redirect('profile:my_rating_and_reviews'), name='profile_root'),
    path('ratings/', views.my_ratings_and_reviews, name='my_rating_and_reviews'),
    path('account/', views.account, name='account'),
    path('statistics/', views.statistics, name='statistics'),
    path('admin_panel/', views.admin_panel, name='admin_panel'),
    path('load_section/', views.load_section, name='load_section'),
    path('logout/', views.custom_logout, name='logout'),
]