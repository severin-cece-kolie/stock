"""Create the first production superuser from environment variables.

This command is intentionally idempotent and safe for production deployment:
- it uses the existing Django authentication model via get_user_model()
- it checks for an existing superuser before creating anything
- it reads credentials from environment variables only
- it never prints or logs the password
"""

import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Create the initial production Django superuser if none exists yet."

    def handle(self, *args, **options):
        User = get_user_model()

        if User.objects.filter(is_superuser=True).exists():
            self.stdout.write(
                self.style.SUCCESS("Production superuser already exists. No action required.")
            )
            return

        required_vars = {
            "ADMIN_USERNAME": "username",
            "ADMIN_EMAIL": "email",
            "ADMIN_PASSWORD": "password",
        }

        missing = [name for name in required_vars if not os.environ.get(name, "").strip()]
        if missing:
            raise CommandError(
                "Missing required environment variable(s) for production admin creation: "
                + ", ".join(missing)
                + ". Define ADMIN_USERNAME, ADMIN_EMAIL and ADMIN_PASSWORD in the deployment environment."
            )

        username = os.environ["ADMIN_USERNAME"].strip()
        email = os.environ["ADMIN_EMAIL"].strip()
        password = os.environ["ADMIN_PASSWORD"]

        if User.objects.filter(username=username).exists():
            raise CommandError(
                "A non-superuser account with the configured ADMIN_USERNAME already exists. "
                "Refusing to overwrite or promote it automatically."
            )

        user = User.objects.create_superuser(
            username=username,
            email=email,
            password=password,
            role=User.Role.ADMIN,
        )

        self.stdout.write(
            self.style.SUCCESS(
                f"Production superuser created successfully: {user.username}"
            )
        )
