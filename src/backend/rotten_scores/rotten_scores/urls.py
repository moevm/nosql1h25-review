from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
    path('profile/', include('user_profile.urls')),
    path('profile/admin_panel', include('admin_panel.urls')),
    path('games/', include('games.urls')),
    path('reviews/', include('reviews.urls')),
]

auth_urls = ([
    path(
        'login/',
        auth_views.LoginView.as_view(),
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

urlpatterns += [path('auth/', include(auth_urls))]
