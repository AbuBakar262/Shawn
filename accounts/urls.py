from rest_framework.routers import DefaultRouter
from django.urls import path, include
from accounts.view.signup_views import SignupModelViewSet
from accounts.view.signin_views import SigninModelViewSet
from accounts.view.signup_views import VerifyViewSet

router = DefaultRouter()

urlpatterns = [
    path('', include(router.urls)),

    # authentication urls for signup and signin and verify email
    path("signup/", SignupModelViewSet.as_view({"post": "create"}), name="signup"),
    path("signin/", SigninModelViewSet.as_view({"post": "create"}), name="signin"),
    path("verify/", VerifyViewSet.as_view({"post": "create"}), name="verify"),
]
