# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand

from apps.users.services.user.gitlab import update_users


class Command(BaseCommand):
    def handle(self, *args, **options):
        update_users()
