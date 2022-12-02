from rest_framework.routers import SimpleRouter
from .views import FriendManagementViewSet
from django.urls import path, include

router = SimpleRouter(trailing_slash=False)
router.register("api/friend", FriendManagementViewSet, basename="friend_management")

urlpatterns = [
    path("", include(router.urls)),
    path("api/contact_list", FriendManagementViewSet.as_view({"get": "contact_list"}), name="contact_list"),
    path("api/all_user_list", FriendManagementViewSet.as_view({"get": "all_user_list"}), name="all_user_list"),
    path("api/send_friend_request", FriendManagementViewSet.as_view({"post": "send_friend_request"}),
         name="send_friend_request"),
    path("api/friend_request_action", FriendManagementViewSet.as_view({"post": "friend_request_action"}),
            name="friend_request_action"),
    path("api/friend_request_delete", FriendManagementViewSet.as_view({"delete": "friend_request_delete"}),
            name="friend_request_delete"),
    path("api/unfriend", FriendManagementViewSet.as_view({"delete": "unfriend"}), name="unfriend"),
]
