from rest_framework.routers import SimpleRouter
from .views import FriendManagementViewSet
from django.urls import path, include

router = SimpleRouter(trailing_slash=False)
router.register("api/friend_management", FriendManagementViewSet, basename="friend_management")

urlpatterns = [
    path("", include(router.urls)),
    path("api/contact_list", FriendManagementViewSet.as_view({"get": "contact_list"}), name="contact_list"),
    path("api/send_friend_request", FriendManagementViewSet.as_view({"post": "send_friend_request"}),
         name="send_friend_request"),
    path("api/friend_request_list", FriendManagementViewSet.as_view({"get": "friend_request_list"}),
         name="friend_request_list"),
]
