from rest_framework.routers import SimpleRouter
from .views import AdminViewSet, ReportUserViewSet, ListReportUserViewSet
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
]
