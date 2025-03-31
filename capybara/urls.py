from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

# Основные URL-маршруты
urlpatterns = [
    path('admin/stats/', include('stats.urls', namespace='stats')), 
    path('admin/', admin.site.urls),
    path('user/', include('user_capybara.urls')),
    path('', include('app.urls')),
    path('api/', include('api.urls')),  
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    
    # Добавление Django Debug Toolbar
    try:
        import debug_toolbar
        urlpatterns.append(path('__debug__/', include(debug_toolbar.urls)))
    except ImportError:
        pass