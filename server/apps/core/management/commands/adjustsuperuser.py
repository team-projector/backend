# -*- coding: utf-8 -*-

import os

from django.contrib.auth.management.commands import createsuperuser
from django.contrib.auth.management.commands.createsuperuser import (
    PASSWORD_FIELD,
)
from django.core.management.base import CommandError


# TODO: use createsuperuser after Django upgraded to 3 version
class Command(createsuperuser.Command):
    """Create superuser in database."""

    def handle(self, *args, **options):  # noqa: WPS110
        """
        Create superuser in Non-interactive mode.

        Use password and username from environment variable, if provided.
        Variables: DJANGO_SUPERUSER_PASSWORD, DJANGO_SUPERUSER_LOGIN
        """
        user_data = {}
        user_data[PASSWORD_FIELD] = os.environ.get("DJANGO_SUPERUSER_PASSWORD")

        username = os.environ.get("DJANGO_SUPERUSER_LOGIN")
        if not username:
            raise CommandError("You must provide DJANGO_SUPERUSER_LOGIN.")

        user_data[self.UserModel.USERNAME_FIELD] = username

        self._fill_user_data_required_fields(user_data, options)

        self.UserModel.objects.create_superuser(**user_data)

        if options["verbosity"] >= 1:
            self.stdout.write("Superuser created successfully.")

    def _fill_user_data_required_fields(self, user_data, options) -> None:
        for field_name in self.UserModel.REQUIRED_FIELDS:
            env_var = "DJANGO_SUPERUSER_{0}".format(field_name.upper())

            username = options[field_name] or os.environ.get(env_var)
            if not username:
                raise CommandError(
                    "You must use --{0} with --noinput.".format(field_name),
                )
            field = self.UserModel._meta.get_field(field_name)  # noqa: WPS437
            user_data[field_name] = field.clean(username, None)
