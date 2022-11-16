from rest_framework.routers import SimpleRouter
from .views import AdminViewSet
from django.urls import path, include

router = SimpleRouter(trailing_slash=False)
router.register("api/admin", AdminViewSet, basename="admin")

urlpatterns = [
    path("", include(router.urls)),
    path("api/admin_login", AdminViewSet.as_view({"post": "login"}), name="admin_login"),
]
