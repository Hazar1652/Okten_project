from rest_framework.routers import DefaultRouter

from .views import TagViewSet, VenueFeatureViewSet, VenueViewSet

router = DefaultRouter()
router.register("venues", VenueViewSet, basename="venues")
router.register("tags", TagViewSet, basename="tags")
router.register("venue-features", VenueFeatureViewSet, basename="venue-features")

urlpatterns = router.urls
