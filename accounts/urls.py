from rest_framework.routers import DefaultRouter
from django.urls import path, include
from accounts.view.signup_views import SignupViewSet
from accounts.view.signin_views import SigninViewSet
from accounts.view.signup_views import VerifyViewSet
from accounts.view.forgot_password_views import ForgotPasswordViewSet, ForgotChangePasswordViewSet
from accounts.view.user_profile_view import ProfileViewSet, ProfileUpdateViewSet

router = DefaultRouter()

urlpatterns = [
    path('', include(router.urls)),

    # authentication urls for signup and signin and verify email
    path("signup/", SignupViewSet.as_view({"post": "create"}), name="signup"),
    path("signin/", SigninViewSet.as_view({"post": "create"}), name="signin"),
    path("verify/", VerifyViewSet.as_view({"post": "create"}), name="verify"),

    # forgot password and change password urls
    path("forgot_password/", ForgotPasswordViewSet.as_view({"post": "forgot_password"}), name="forgot_password"),
    path("forgot_change_password/<uidb64>/<token>/",
         ForgotChangePasswordViewSet.as_view({"post": "forgot_change_password"}),
         name="forgot_change_password"),

    # user profile retrieve and update urls
    path("profile/", ProfileViewSet.as_view({"post": "profile_details"}), name="profile_details"),
    path("profile_update/", ProfileUpdateViewSet.as_view({"put": "profile_update"}), name="profile_update"),
]
