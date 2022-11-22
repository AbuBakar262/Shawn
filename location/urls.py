from rest_framework.routers import SimpleRouter
from .views import *
from django.urls import path, include

router = SimpleRouter(trailing_slash=False)
router.register("api/location", UserLocationViewSet, basename="location")
router.register("api/check-in-location", CheckInLocationViewSet, basename="check-in-location")

urlpatterns = [
    path("", include(router.urls)),
]
