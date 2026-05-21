from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("core.urls")),
    path("api/", include("apps.users.urls")),
    path("api/", include("apps.venues.urls")),
    path("api/", include("apps.reviews.urls")),
    path("api/", include("apps.favorites.urls")),
    path("api/", include("apps.news.urls")),
    path("api/", include("apps.hangout.urls")),
    path("api/", include("apps.analytics.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
