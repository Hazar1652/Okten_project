from rest_framework.routers import DefaultRouter

from .views import HangoutViewSet

router = DefaultRouter()
router.register("hangouts", HangoutViewSet, basename="hangouts")

urlpatterns = router.urls
