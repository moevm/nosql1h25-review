from django.urls import path
from . import views

app_name = 'profile'

urlpatterns = [
    path('', views.my_reviews_and_reviews, name='my_rating_and_reviews'),
    path('account/', views.account, name='account'),
    path('statistics/', views.statistics, name='statistics'),
    path('admin_panel/',views.admin_panel, name='admin_panel'),
    path('load_section/', views.load_section, name='load_section'),
]