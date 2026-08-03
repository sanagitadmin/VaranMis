from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.exceptions import PermissionDenied


ROLE_ADMIN = "Admin"
ROLE_REGISTRAR = "Registrar"
ROLE_VIEWER = "Viewer"


def has_role(user, role):
    return user.is_authenticated and user.groups.filter(name=role).exists()


def can_view(user):
    return user.is_authenticated and (
        user.is_superuser or has_role(user, ROLE_ADMIN) or has_role(user, ROLE_REGISTRAR) or has_role(user, ROLE_VIEWER)
    )


def can_register(user):
    return user.is_authenticated and (user.is_superuser or has_role(user, ROLE_ADMIN) or has_role(user, ROLE_REGISTRAR))


def can_manage(user):
    return user.is_authenticated and (user.is_superuser or has_role(user, ROLE_ADMIN))


def view_required(view_func):
    return login_required(user_passes_test(can_view, login_url="login")(view_func))


def register_required(view_func):
    return login_required(user_passes_test(can_register, login_url="login")(view_func))


def admin_required(view_func):
    return login_required(user_passes_test(can_manage, login_url="login")(view_func))


def require_admin_role(request):
    if not can_manage(request.user):
        raise PermissionDenied
