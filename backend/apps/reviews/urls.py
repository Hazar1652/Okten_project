from rest_framework.routers import DefaultRouter

from .views import ComplaintViewSet, ReviewViewSet

router = DefaultRouter()
router.register("reviews", ReviewViewSet, basename="reviews")
router.register("complaints", ComplaintViewSet, basename="complaints")

urlpatterns = router.urls
