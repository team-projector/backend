# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand

from apps.development.services.project.gitlab import load_projects


class Command(BaseCommand):
    def handle(self, *args, **options):
        load_projects()
