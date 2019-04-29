from django.core.management.base import BaseCommand

from apps.development.services.loaders import update_users


class Command(BaseCommand):
    def handle(self, *args, **options):
        update_users()
