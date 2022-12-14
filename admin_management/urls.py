from rest_framework.routers import SimpleRouter
from .views import (
    AdminViewSet, ReportUserViewSet, ListReportUserViewSet, AdminListUserViewSet, SearchUserViewSet
)
from django.urls import path, include

router = SimpleRouter(trailing_slash=False)
router.register("api/admin", AdminViewSet, basename="admin")

urlpatterns = [
    path("", include(router.urls)),
    path("api/admin_login", AdminViewSet.as_view({"post": "login"}), name="admin_login"),
    path("api/report_user", ReportUserViewSet.as_view({"post": "create"}), name='report_user'),
    path("api/report_user_list", ListReportUserViewSet.as_view({"get": "list"}), name='report_user_list'),
    path("api/get_report_by_id", ListReportUserViewSet.as_view({"get": "get_by_id"}), name='get_report_by_id'),
    path("api/update_report", ReportUserViewSet.as_view({"put": "update"}), name='update_report'),

    # User Listing for Admin urls
    path('api/subscribed_user_list', AdminListUserViewSet.as_view({'get': 'subscribed_user_list'}),
         name='subscribed_user_list'),
    path('api/unsubscribed_user_list', AdminListUserViewSet.as_view({'get': 'unsubscribed_user_list'}),
         name='subscribed_user_list'),
    path('api/trial_user_list', AdminListUserViewSet.as_view({'get': 'trial_user_list'}),
         name='trial_user_list'),
    path('api/list_all_users', AdminListUserViewSet.as_view({'get': 'list_all_users'}),
         name='list_all_users'),

    # Search User for Admin urls
    path('api/search_subs_user', SearchUserViewSet.as_view({'get': 'search_subs_user'}), name='search_subs_user'),
    path('api/search_unsubs_user', SearchUserViewSet.as_view({'get': 'search_unsubs_user'}), name='search_unsubs_user'),
    path('api/search_trial_user', SearchUserViewSet.as_view({'get': 'search_trial_user'}), name='search_trial_user'),
    path('api/search_all_user', SearchUserViewSet.as_view({'get': 'search_all_user'}), name='search_all_user'),
]
