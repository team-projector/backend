# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand

from apps.development.services.issue.gl.manager import IssueGlManager


class Command(BaseCommand):
    def handle(self, *args, **options):
        IssueGlManager().sync_issues(True)
