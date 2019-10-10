# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand

from apps.development.services.merge_request.gitlab import load_merge_requests


class Command(BaseCommand):
    def handle(self, *args, **options):
        load_merge_requests(True)
