from rest_framework.routers import SimpleRouter
from .views import DeviceRegistrationViewSet
from django.urls import path, include

router = SimpleRouter(trailing_slash=False)
router.register("api/device", DeviceRegistrationViewSet, basename="device")

urlpatterns = [
    path("", include(router.urls)),
]