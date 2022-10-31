from rest_framework.routers import DefaultRouter
from django.urls import path, include
from accounts.view.signup_views import SignupViewSet
from accounts.view.signin_views import SigninViewSet
from accounts.view.signup_views import VerifyViewSet
from accounts.view.forgot_password_views import ForgotPasswordViewSet, ForgotChangePasswordViewSet
from accounts.view.user_profile_view import ProfileViewSet, ProfileUpdateViewSet
from accounts.view.friend_request_views import FriendRequestViewSet
from accounts.view.friendship_views import FriendsViewSet

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
    path("profile_list/", ProfileViewSet.as_view({"get": "profile_list"}), name="profile_list"),
    path("profile_details/", ProfileViewSet.as_view({"post": "profile_details"}), name="profile_details"),
    path("profile_update/", ProfileUpdateViewSet.as_view({"put": "profile_update"}), name="profile_update"),
    path("profle_delete/", ProfileViewSet.as_view({"delete": "destroy_profile"}), name="destroy_profile"),

    # friend request urls
    path("send_friend_request/", FriendRequestViewSet.as_view({"post": "send_friend_request"}),
         name="send_friend_request"),
    path("friend_request_list/", FriendRequestViewSet.as_view({"get": "friend_request_list"}),
         name="friend_request_list"),
    path("friend_request_action/", FriendRequestViewSet.as_view({"post": "friend_request_action"}),
         name="friend_request_action"),
    path("friend_request_delete/", FriendRequestViewSet.as_view({"delete": "friend_request_delete"}),
         name="friend_request_delete"),

    # friend list urls
    path("friend_list/", FriendsViewSet.as_view({"get": "friend_list"}), name="friend_list"),
    path("friend_delete/", FriendsViewSet.as_view({"delete": "friend_delete"}), name="friend_delete"),
]
