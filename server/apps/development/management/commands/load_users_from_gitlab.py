from django.core.management.base import BaseCommand

from apps.development.utils.loaders import load_users


class Command(BaseCommand):
    def handle(self, *args, **options):
        load_users()
