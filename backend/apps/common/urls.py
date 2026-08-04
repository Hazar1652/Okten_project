from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .cms_views import SitePageViewSet, TopCategoryViewSet

router = DefaultRouter()
router.register("pages", SitePageViewSet, basename="site-pages")
router.register("top-categories", TopCategoryViewSet, basename="top-categories")

urlpatterns = [
    path("", include(router.urls)),
]
