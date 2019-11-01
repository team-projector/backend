# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand

from apps.users.services.user.gl.manager import UserGlManager


class Command(BaseCommand):
    def handle(self, *args, **options):
        UserGlManager().sync_users()
