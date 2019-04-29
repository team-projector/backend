from django.core.management.base import BaseCommand

from apps.development.services.loaders import load_projects


class Command(BaseCommand):
    def handle(self, *args, **options):
        load_projects()
