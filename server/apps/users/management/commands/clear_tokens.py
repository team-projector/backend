from django.core.management.base import BaseCommand

from apps.users.services.token import clear_tokens


class Command(BaseCommand):
    def handle(self, *args, **options):
        clear_tokens()
