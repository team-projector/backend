# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand

from apps.development.services.gitlab.issues import load_issues


class Command(BaseCommand):
    def handle(self, *args, **options):
        load_issues(True)
