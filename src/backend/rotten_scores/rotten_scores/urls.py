from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from core import forms


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include(('core.urls', 'core'), namespace='core')),
    path('profile/', include(('user_profile.urls', 'user_profile'), namespace='user_profile')),
    path('profile/admin_panel/', include(('admin_panel.urls', 'admin_panel'), namespace='admin_panel')),
    path('games/', include(('games.urls', 'games'), namespace='games')),
    path('reviews/', include(('reviews.urls', 'reviews'), namespace='reviews')),
]

auth_urls = ([
    path(
        'login/',
        auth_views.LoginView.as_view(
            authentication_form=forms.EmailAuthenticationForm,
        ),
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