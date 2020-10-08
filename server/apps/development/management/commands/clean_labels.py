from typing import Any, Tuple

from django.core.management import BaseCommand
from tqdm import tqdm

from apps.core.gitlab.client import get_default_gitlab_client
from apps.development.services.gl.labels.cleaner import LabelsCleaner, Project


class Command(BaseCommand):
    """Cleanup labels."""

    def add_arguments(self, parser):
        """Add call arguments."""
        parser.add_argument(
            "--group",
            type=str,
            help="Gitlab group_id for sync labels",
        )
        parser.add_argument(
            "-l",
            "--log",
            action="store_true",
            default=False,
            help="Show only log, without apply",
        )

    def handle(self, *args, **options) -> None:  # noqa: WPS110, WPS210
        """Call function."""
        self._parse_params(*args, **options)
        client = get_default_gitlab_client()

        operations = self._generate_operations(client)

        if self.only_log:
            return

        with tqdm(total=len(operations), desc="Executing operations") as pbar:
            for num, operation in enumerate(operations, start=1):
                method, args, kwargs = operation

                try:
                    client.http_request(method, *args, **kwargs)

                except Exception:
                    self.stdout(
                        "Failed on {0} operation: {1}".format(num, operation),
                    )

                    self.stdout(
                        "Left operations:\n {0}".format(
                            "\n".join(operations[num:]),
                        ),
                    )
                pbar.update()

    def _generate_operations(self, client) -> Tuple[Any, ...]:  # type: ignore
        """
        Generate operations.

        :param client:
        :rtype: Tuple[Any, __Ellipsis__]
        """
        total = self._get_total(client)
        cleaner = LabelsCleaner(client=client)

        with tqdm(total=total, desc="Generating operations") as pbar:
            original_f = Project._adjust_labels_for_single_item  # noqa: WPS437

            def _wrapped(proj, gl_api_obj):  # noqa:WPS430
                """
                Wrapped.

                :param proj:
                :param gl_api_obj:
                """
                original_f(proj, gl_api_obj)
                pbar.update()

            Project._adjust_labels_for_single_item = _wrapped  # noqa: WPS437

            return cleaner.clean_group(self.group_for_sync, dry_run=True)

    def _get_total(self, client) -> int:
        """
        Get total.

        :param client:
        :rtype: int
        """
        gr = client.groups.get(self.group_for_sync)
        stats = client.http_get("/groups/{0}/issues_statistics".format(gr.id))
        issues_count = stats.get("statistics").get("counts").get("all")
        mergerequests = gr.mergerequests.list(all=True)
        return len(mergerequests) + issues_count

    def _parse_params(self, *args, **options) -> None:
        """
        Parse params.

        :rtype: None
        """
        self.group_for_sync = options.get("group")
        self.only_log = options.get("log")
