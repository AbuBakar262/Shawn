from rest_framework.routers import SimpleRouter
from .views import *
from django.urls import path, include

router = SimpleRouter(trailing_slash=False)
router.register("api/device", DeviceRegistrationViewSet, basename="device")
router.register("api/notification", NotificationViewSet, basename="notification")

urlpatterns = [
    path("", include(router.urls)),
]