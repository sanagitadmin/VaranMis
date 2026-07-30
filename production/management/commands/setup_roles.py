from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand

from production.permissions import ROLE_ADMIN, ROLE_REGISTRAR, ROLE_VIEWER


class Command(BaseCommand):
    help = "Create application roles and starter users."

    def handle(self, *args, **options):
        admin_group, _ = Group.objects.get_or_create(name=ROLE_ADMIN)
        registrar_group, _ = Group.objects.get_or_create(name=ROLE_REGISTRAR)
        viewer_group, _ = Group.objects.get_or_create(name=ROLE_VIEWER)

        User = get_user_model()
        admin, _ = User.objects.get_or_create(username="admin", defaults={"email": "admin@local.local"})
        admin.is_staff = True
        admin.is_superuser = True
        admin.set_password("Admin@12345")
        admin.save()
        admin.groups.add(admin_group)

        registrar, _ = User.objects.get_or_create(username="registrar", defaults={"email": "registrar@local.local"})
        registrar.is_staff = False
        registrar.is_superuser = False
        registrar.set_password("Registrar@12345")
        registrar.save()
        registrar.groups.add(registrar_group)

        viewer, _ = User.objects.get_or_create(username="viewer", defaults={"email": "viewer@local.local"})
        viewer.is_staff = False
        viewer.is_superuser = False
        viewer.set_password("Viewer@12345")
        viewer.save()
        viewer.groups.add(viewer_group)

        self.stdout.write(self.style.SUCCESS("Roles and starter users are ready."))
