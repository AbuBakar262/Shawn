from rest_framework.routers import SimpleRouter
from .views import *
from django.urls import path, include

router = SimpleRouter(trailing_slash=False)
router.register("api/location", UserLocationViewSet, basename="location")
router.register("api/check_in_location", CheckInLocationViewSet, basename="check_in_location")

urlpatterns = [
    path("", include(router.urls)),
    path("api/search_location", UserLocationViewSet.as_view({"get": "search_location"}), name="search_location"),
    path("api/location_checkin", CheckInLocationViewSet.as_view({"get": "location_checkin"}), name="location_checkin"),
]
