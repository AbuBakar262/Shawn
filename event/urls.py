from rest_framework.routers import SimpleRouter
from .views import UserLocationViewSet
from django.urls import path, include

router = SimpleRouter(trailing_slash=False)
router.register("api/event", UserLocationViewSet, basename="event")

urlpatterns = [
    path("", include(router.urls)),
    path("api/save_location", UserLocationViewSet.as_view({"post": "save_location"}), name="save_location"),
    path("api/saved_locations", UserLocationViewSet.as_view({"get": "saved_locations"}), name="saved_locations"),
    path("api/get_location", UserLocationViewSet.as_view({"get": "get_location"}), name="get_location"),
    path("api/delete_location", UserLocationViewSet.as_view({"delete": "delete_location"}), name="delete_location"),
]
