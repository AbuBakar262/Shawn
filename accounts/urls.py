from rest_framework.routers import SimpleRouter
from .views import UserViewSet
from django.urls import path, include

router = SimpleRouter(trailing_slash=False)
router.register("api/user", UserViewSet, basename="signup")

urlpatterns = [
    path("", include(router.urls)),
    path("api/signup", UserViewSet.as_view({"post": "signup"}), name="signup"),
    path("api/create_profile", UserViewSet.as_view({"post": "create_profile"}), name="create_profile"),
    path("api/login", UserViewSet.as_view({"post": "login"}), name="login"),
]
