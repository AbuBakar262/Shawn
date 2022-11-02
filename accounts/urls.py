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
    path("api/forgot_password", UserViewSet.as_view({"post": "forgot_password"}), name="forgot_password"),
    path("api/forgot_change_password/<uidb64>/<token>/", UserViewSet.as_view({"post": "forgot_change_password"}),
         name="forgot_change_password"),
]
