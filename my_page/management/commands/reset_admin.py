from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
import os


class Command(BaseCommand):
    help = "Temporarily reset the admin password"

    def handle(self, *args, **options):
        User = get_user_model()

        username = "k3r3nr3a77"
        password = os.getenv("ADMIN_RESET_PASSWORD")

        if not password:
            self.stdout.write(
                self.style.ERROR("ADMIN_RESET_PASSWORD is not configured.")
            )
            return

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f"User '{username}' does not exist.")
            )
            return

        user.set_password(password)
        user.save()

        self.stdout.write(
            self.style.SUCCESS(
                f"Password successfully reset for '{username}'."
            )
        )