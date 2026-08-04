from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .admin_views import UserAdminViewSet
from .views import MeView

router = DefaultRouter()
router.register("users/admin", UserAdminViewSet, basename="users-admin")

urlpatterns = [
    path("users/me/", MeView.as_view(), name="users-me"),
    path("", include(router.urls)),
]
