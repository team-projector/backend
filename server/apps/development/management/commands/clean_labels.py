# -*- coding: utf-8 -*-

from django.core.management import BaseCommand
from tqdm import tqdm

from apps.core.gitlab.client import get_default_gitlab_client
from apps.development.services.gl.labels import LabelsCleaner


class Command(BaseCommand):
    """Cleanup labels."""

    def add_arguments(self, parser):
        """Add call arguments."""
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
            help='Show only log, without apply',
        )

    def handle(self, *args, **options):  # noqa: WPS110
        """Call function."""
        self._parse_params(*args, **options)
        client = get_default_gitlab_client()

        gr = client.groups.get(self.group_for_sync)
        stats = client.http_get('/groups/{0}/issues_statistics'.format(gr.id))
        issues_count = stats.get('statistics').get('counts').get('all')
        mergerequests = gr.mergerequests.list(all=True)
        total = len(mergerequests) + issues_count

        cleaner = LabelsCleaner(client=client)

        with tqdm(total=total) as pbar:
            cleaner.clean_group(
                self.group_for_sync,
                adjust_element_callback=pbar.update,
                dry_run=self.only_log,
            )

    def _parse_params(self, *args, **options) -> None:
        self.group_for_sync = options.get('group')
        self.only_log = options.get('log')
