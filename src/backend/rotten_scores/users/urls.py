from django.urls import path
from . import views

urlpatterns = [
    path('account/', views.account_view, name='account'),
    path('account/edit/', views.edit_account, name='edit_account'),
    path('account/statistics/', views.statistics_view, name='statistics'),
    path('account/my-reviews/', views.my_reviews, name='my_reviews'),
]
