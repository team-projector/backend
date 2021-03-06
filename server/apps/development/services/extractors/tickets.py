import re
from typing import List, Pattern

from django.conf import settings


class _Extractor:
    def __new__(cls) -> "_Extractor":
        """Singleton for regex speed improvement."""
        if not hasattr(cls, "instance"):  # noqa: WPS421
            cls.instance = super().__new__(cls)
        return cls.instance

    def __init__(self) -> None:
        """
        Init.

        :rtype: None
        """
        self.re_ticket: Pattern[str] = re.compile(
            r"{0}/([^/]+/manager/milestones/\d+;ticket=|tickets/)(?P<ticket_id>\d+)".format(  # noqa: E501
                settings.DOMAIN_NAME,
            ),
        )

    def extract(self, text: str) -> List[str]:
        """
        Extract.

        :param text:
        :type text: str
        :rtype: List[str]
        """
        if not text:
            return []

        return list(
            {
                match.groupdict()["ticket_id"]
                for match in self.re_ticket.finditer(text)
            },
        )


def extract_tickets_links(text: str) -> List[str]:
    """Extract tickets links from content."""
    return _Extractor().extract(text)
