# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand

from apps.development.services.merge_request.gl.manager import (
    MergeRequestGlManager,
)


class Command(BaseCommand):
    def handle(self, *args, **options):
        MergeRequestGlManager().sync_merge_requests(True)
