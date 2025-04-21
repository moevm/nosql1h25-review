from django.contrib.auth.views import LogoutView
from django.urls import path
from . import views

app_name = "core"

urlpatterns = [
    path('', views.HomepageView.as_view(), name='homepage'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('database/', views.database_view, name='database'),
]