# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand

from apps.development.models import Label


class Command(BaseCommand):
    def handle(self, *args, **options):
        deleted, _ = Label.objects.filter(
            merge_requests__isnull=True, issues__isnull=True
        ).delete()
        self.stdout.write('{0} labels were removed.'.format(deleted))
