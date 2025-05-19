from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views

from src.backend.core.views import LoginView


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include(('backend.core.urls', 'backend.core'), namespace='core')),
    path('profile/', include(('backend.user_profile.urls', 'backend.user_profile'), namespace='user_profile')),
    path('games/', include(('backend.games.urls', 'backend.games'), namespace='games')),
    path('reviews/', include(('backend.reviews.urls', 'backend.reviews'), namespace='reviews')),
]

auth_urls = ([
    path(
        'login/',
        LoginView.as_view(),
        name='login',
    ),
    path(
        'logout/',
        auth_views.LogoutView.as_view(
            template_name='registration/logout.html'
        ),
        name='logout',
    ),
], 'users')

urlpatterns += [
    path('auth/', include(auth_urls, namespace='users')),
]