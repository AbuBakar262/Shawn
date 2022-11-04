from rest_framework.routers import SimpleRouter
from .views import UserViewSet, ProfileViewSet, SocialViewSet
from django.urls import path, include

router = SimpleRouter(trailing_slash=False)
router.register("api/user", UserViewSet, basename="signup")
router.register("api/profile", ProfileViewSet, basename="profile")

urlpatterns = [
    path("", include(router.urls)),
    path("api/signup", UserViewSet.as_view({"post": "signup"}), name="signup"),
    path("api/create_profile", UserViewSet.as_view({"post": "create_profile"}), name="create_profile"),
    path("api/login", UserViewSet.as_view({"post": "login"}), name="login"),
    path("api/forgot_password", UserViewSet.as_view({"post": "forgot_password"}), name="forgot_password"),
    path("api/reset_password/<uidb64>/<token>/", UserViewSet.as_view({"post": "reset_password"}),
         name="reset_password"),

    # User Profile
    path("api/profile_details", ProfileViewSet.as_view({"get": "profile_details"}), name="profile_details"),
    path("api/profile_edit", ProfileViewSet.as_view({"put": "profile_edit"}), name="profile_edit"),
    path("api/profile_list", ProfileViewSet.as_view({"get": "profile_list"}), name="profile_list"),
    path("api/profile_delete", ProfileViewSet.as_view({"delete": "profile_delete"}), name="profile_delete"),

    # Social Login
    path("api/social_login", SocialViewSet.as_view({"post": "social_login"}), name="social_login"),
    path("api/social_profile_create", SocialViewSet.as_view({"post": "social_profile_create"}),
         name="social_profile_create")
]
