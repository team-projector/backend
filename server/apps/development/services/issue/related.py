from typing import List
from urllib.parse import urlparse

from django.db.models import QuerySet

from apps.development.models.issue import Issue
from apps.development.models.note import NoteType
from apps.development.services.extractors import extract_issue_links


def get_related_issues(issue: Issue) -> QuerySet:
    """Getting related issues."""
    links = extract_issue_links(issue.description, issue)
    links += sum(
        (
            note.data.get("issues", [])
            for note in issue.notes.all()
            if note.type == NoteType.COMMENT and note.data
        ),
        [],
    )

    links = _add_alternative_urls(links)

    return Issue.objects.filter(gl_url__in=links)


def _add_alternative_urls(links) -> List[str]:
    """
    Add alternative urls.

    :param links:
    :rtype: List[str]
    """
    alt_links = [_get_alternative_link(link) for link in links]
    return [*links, *alt_links]


def _get_alternative_link(link: str) -> str:
    """
    Get alternative link.

    :param link:
    :type link: str
    :rtype: str
    """
    parsed = urlparse(link)
    web_url_path = "/".join(parsed.path.split("/")[:-1])

    return (
        link.replace("/-/issues", "/issues")
        if web_url_path.endswith("/-/issues")
        else link.replace("/issues", "/-/issues")
    )
