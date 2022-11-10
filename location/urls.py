from rest_framework.routers import SimpleRouter
from .views import UserLocationViewSet
from django.urls import path, include

router = SimpleRouter(trailing_slash=False)
router.register("api/location", UserLocationViewSet, basename="location")

urlpatterns = [
    path("", include(router.urls)),
]
