from django.core.management import BaseCommand

from apps.core.gitlab.client import get_default_gitlab_client
from apps.development.services.gl.labels import LabelsCleaner


class Command(BaseCommand):
    def _parse_params(self, *args, **options):
        self.group_for_sync = options.get('group')
        self.only_log = options.get('log')

    def add_arguments(self, parser):
        parser.add_argument(
            '--group',
            type=str,
            help='Gitlab group_id for sync labels',
        )
        parser.add_argument(
            '-l',
            '--log',
            action='store_true',
            default=False,
            help='Show only log, without apply'
        )

    def handle(self, *args, **options):
        self._parse_params(*args, **options)

        cleaner = LabelsCleaner(client=get_default_gitlab_client())
        cleaner.clean_group(self.group_for_sync, self.only_log)
