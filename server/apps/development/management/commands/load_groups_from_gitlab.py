# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand

from apps.development.services.gitlab.groups import load_groups


class Command(BaseCommand):
    def handle(self, *args, **options):
        load_groups()
