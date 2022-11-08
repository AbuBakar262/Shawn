from rest_framework.routers import SimpleRouter
from .views import EventViewSet
from django.urls import path, include

router = SimpleRouter(trailing_slash=False)
router.register("api/event", EventViewSet, basename="event")

urlpatterns = [
    path("", include(router.urls)),
    path("all_events", EventViewSet.as_view({"get": "all_events"}), name="all_events"),
    path("get_event/<pk>", EventViewSet.as_view({"get": "get_event"}), name="get_event"),
]
