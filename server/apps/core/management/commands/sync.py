from django.core.management.base import BaseCommand

from apps.development.tasks import sync_issues


class Command(BaseCommand):
    def handle(self, *args, **options):
        sync_issues()

