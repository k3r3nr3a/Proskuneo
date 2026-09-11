from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
import os


class Command(BaseCommand):
    help = "Create or reset the admin user"

    def handle(self, *args, **options):
        User = get_user_model()

        username = "k3r3nr3a77"
        password = os.getenv("ADMIN_RESET_PASSWORD")

        if not password:
            self.stdout.write(
                self.style.ERROR("ADMIN_RESET_PASSWORD is not configured.")
            )
            return

        user, created = User.objects.get_or_create(
            username=username,
            defaults={
                "is_staff": True,
                "is_superuser": True,
                "is_active": True,
            },
        )

        if created:
            user.set_password(password)
            user.save()

            self.stdout.write(
                self.style.SUCCESS(
                    f"Admin user '{username}' created successfully."
                )
            )
        else:
            user.is_staff = True
            user.is_superuser = True
            user.is_active = True
            user.set_password(password)
            user.save()

            self.stdout.write(
                self.style.SUCCESS(
                    f"Admin user '{username}' password reset successfully."
                )
            )