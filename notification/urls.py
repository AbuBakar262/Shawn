from rest_framework.routers import SimpleRouter
from .views import *
from django.urls import path, include

router = SimpleRouter(trailing_slash=False)
router.register("api/device", DeviceRegistrationViewSet, basename="device")
router.register("api/notification", NotificationViewSet, basename="notification")

urlpatterns = [
    path("", include(router.urls)),
    path("api/total_notifications", NotificationViewSet.as_view({"get": "total_notifications"}), name="total_notifications"),
    path("api/notification_active", NotificationViewSet.as_view({"post": "notification_active"}), name="notification_active"),
]