from rest_framework.routers import SimpleRouter
from .views import SubscriptionViewSet
from django.urls import path, include

router = SimpleRouter(trailing_slash=False)
router.register("api/subscription", SubscriptionViewSet, basename="subscription")

urlpatterns = [
    path("", include(router.urls)),
]