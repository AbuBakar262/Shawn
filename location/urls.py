from rest_framework.routers import SimpleRouter
from .views import *
from django.urls import path, include

router = SimpleRouter(trailing_slash=False)
router.register("api/location", UserLocationViewSet, basename="location")
router.register("api/check_in_location", CheckInLocationViewSet, basename="check_in_location")

urlpatterns = [
    path("", include(router.urls)),
    path(
        "api/search_location",
        SearchLocation.as_view(),
        name="search_location",
        ),
]
