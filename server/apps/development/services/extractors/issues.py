# -*- coding: utf-8 -*-

import re
from typing import List, Pattern, Union
from urllib.parse import urlparse

from django.conf import settings

from apps.development.models import MergeRequest
from apps.development.models.issue import Issue


class _Extractor:
    def __new__(cls) -> "_Extractor":
        """Singleton for regex speed improvement."""
        if not hasattr(cls, "instance"):  # noqa: WPS421
            cls.instance = super().__new__(cls)
        return cls.instance

    def __init__(self) -> None:
        self.re_issue_number: Pattern[str] = re.compile(
            r"(^|\s)(#(?P<issue_number>\d+))(\s|[^\w]|$)",
        )

        self.re_gitlab_issue_link: Pattern[str] = re.compile(
            r"(?P<issue_link>{0}.*/issues/\d+)".format(
                settings.GITLAB_ADDRESS,
            ),
        )

    def extract(
        self, text: str, work_item: Union[Issue, MergeRequest] = None,
    ) -> List[str]:
        if not text:
            return []

        links = []
        links += self.re_gitlab_issue_link.findall(text)
        if work_item:
            issues_numbers = [
                match[2] for match in self.re_issue_number.findall(text)
            ]
            links += self._iids_to_links(work_item, issues_numbers)

        return list(set(links))

    def _iids_to_links(self, work_item, iids) -> List[str]:
        parsed = urlparse(work_item.gl_url)
        url_template = "{0}://{1}{2}/{{0}}".format(
            parsed.scheme,
            parsed.hostname,
            "/".join(parsed.path.split("/")[:-1]),
        )

        return [url_template.format(iid) for iid in iids]


def extract_issue_links(text: str, issue: Issue = None) -> List[str]:
    """Extract issues links from content."""
    return _Extractor().extract(text, issue)
