from rest_framework.routers import SimpleRouter
from .views import UserViewSet, ProfileViewSet, SocialViewSet, BlockUserViewSet
from django.urls import path, include

router = SimpleRouter(trailing_slash=False)
router.register("api/user", UserViewSet, basename="signup")
router.register("api/profile", ProfileViewSet, basename="profile")

urlpatterns = [
    path("", include(router.urls)),
    path("api/signup", UserViewSet.as_view({"post": "signup"}), name="signup"),
    path("api/login", UserViewSet.as_view({"post": "login"}), name="login"),

    path("api/forgot_password", UserViewSet.as_view({"post": "forgot_password"}), name="forgot_password"),
    path("api/verify_otp", UserViewSet.as_view({"post": "verify_otp"}), name="verify_otp"),
    path("api/reset_password", UserViewSet.as_view({"post": "reset_password"}),
         name="reset_password"),

    # User Profile
    path("api/user_profile", ProfileViewSet.as_view({"get": "user_profile"}), name="user_profile"),
    path("api/profile_status", ProfileViewSet.as_view({"post": "profile_status"}), name="profile_status"),

    # Social Login
    path("api/social_signup", SocialViewSet.as_view({"post": "social_signup"}), name="social_signup"),
    path("api/social_login", SocialViewSet.as_view({"post": "social_login"}), name="social_login"),

    # Block User
    path("api/block_user", BlockUserViewSet.as_view({"post": "block_user"}), name="block_user"),
    path("api/blocked_user_list", BlockUserViewSet.as_view({"get": "blocked_user_list"}), name="blocked_user_list"),
    path("api/unblock_user", BlockUserViewSet.as_view({"delete": "unblock_user"}), name="unblock_user"),
]
