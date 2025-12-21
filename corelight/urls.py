from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='index'),
    path('accounts/', include('django.contrib.auth.urls')),  # логин, пароль и т.д.
    path('register/', views.register, name='register'),
    path('player/', views.player_character, name='player_character'),
    path('game/', include('game.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler404 = 'corelight.views.handler404'
handler403 = 'corelight.views.handler403'
handler500 = 'corelight.views.handler500'