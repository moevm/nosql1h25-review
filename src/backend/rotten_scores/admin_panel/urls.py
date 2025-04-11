from django.urls import path
from . import views

urlpatterns = [
    path('', views.import_export, name='import_export'),
]
