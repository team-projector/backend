# -*- coding: utf-8 -*-

import getpass
import os
import sys

from django.contrib.auth.management import get_default_username
from django.contrib.auth.management.commands import createsuperuser
from django.contrib.auth.management.commands.createsuperuser import (
    PASSWORD_FIELD,
    NotRunningInTTYException,
)
from django.contrib.auth.password_validation import validate_password
from django.core import exceptions
from django.core.management.base import CommandError
from django.utils.text import capfirst


# TODO: use createsuperuser after Django upgraded to 3 version
class Command(createsuperuser.Command):
    def handle(self, *args, **options):
        """
        Create superuser in Non-interactive mode.

        Use password and username from environment variable, if provided.
        Variables: DJANGO_SUPERUSER_PASSWORD, DJANGO_SUPERUSER_LOGIN
        """
        user_data = {}
        user_data[PASSWORD_FIELD] = os.environ.get('DJANGO_SUPERUSER_PASSWORD')

        username = os.environ.get('DJANGO_SUPERUSER_LOGIN')
        if not username:
            raise CommandError('You must provide DJANGO_SUPERUSER_LOGIN')

        user_data[self.UserModel.USERNAME_FIELD] = username

        for field_name in self.UserModel.REQUIRED_FIELDS:
            env_var = 'DJANGO_SUPERUSER_' + field_name.upper()
            value = options[field_name] or os.environ.get(env_var)
            if not value:
                raise CommandError('You must use --%s with --noinput.' % field_name)
            field = self.UserModel._meta.get_field(field_name)
            user_data[field_name] = field.clean(value, None)

        database = options['database']
        self.UserModel._default_manager.db_manager(database).create_superuser(**user_data)

        if options['verbosity'] >= 1:
            self.stdout.write("Superuser created successfully.")
