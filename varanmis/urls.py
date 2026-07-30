from django.contrib import admin
from django.urls import include, path

from production.permissions import can_manage


def admin_has_permission(request):
    return request.user.is_active and request.user.is_staff and can_manage(request.user)


admin.site.has_permission = admin_has_permission


urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("django.contrib.auth.urls")),
    path("", include("production.urls")),
]
