from .permissions import can_manage, can_register, can_view


def roles(request):
    user = request.user
    return {
        "can_view_reports": can_view(user),
        "can_register_reports": can_register(user),
        "can_manage_settings": can_manage(user),
    }
