# -*- coding: utf-8 -*-

from typing import List, Tuple
from urllib.parse import urlparse

from django.db.models import QuerySet

from apps.development.models.issue import Issue
from apps.development.models.note import NoteType
from apps.development.services.note.gl.parsers.base import (
    RE_GITLAB_ISSUE_LINK,
    RE_ISSUE_NUMBER,
)


def adjust_issue_ticket(issue: Issue) -> None:
    """Setting issue.ticket from related issues."""
    if issue.ticket:
        return

    related_issue = (
        get_related_issues(issue)
        .exclude(pk=issue.pk)
        .filter(ticket_id__isnull=False)
        .first()
    )

    if related_issue:
        issue.ticket = related_issue.ticket


def get_related_issues(issue: Issue) -> QuerySet:
    """Getting related issues."""
    links = [
        *_get_related_issues_by_notes(issue),
        *_get_related_issues_by_description(issue),
    ]

    return Issue.objects.filter(gl_url__in=links)


def _get_related_issues_by_notes(issue) -> List[str]:
    iids = []
    links = []

    notes = (
        note
        for note in issue.notes.all()
        if note.type == NoteType.COMMENT and note.data
    )

    for note in notes:
        iids += note.data.get("numbers", [])
        links += note.data.get("links", [])

    links += _iids_to_links(issue, iids)

    return links


def _get_related_issues_by_description(issue) -> List[str]:
    iids = [
        match[2] for match in RE_ISSUE_NUMBER.findall(issue.description or "")
    ]

    links = RE_GITLAB_ISSUE_LINK.findall(issue.description or "")
    links += _iids_to_links(issue, iids)

    return links


def _iids_to_links(issue, iids) -> List[str]:
    url_template, alt_url_template = _get_project_issue_url_templates(issue)
    links = []

    for iid in iids:
        links.append(url_template.format(iid))
        links.append(alt_url_template.format(iid))

    return links


def _get_project_issue_url_templates(issue) -> Tuple[str, str]:
    parsed = urlparse(issue.gl_url)
    web_url_path = "/".join(parsed.path.split("/")[:-1])

    if web_url_path.endswith("/-/issues"):
        alt_web_url_path = web_url_path.replace("/-/", "/")
    else:
        alt_web_url_path = web_url_path.replace("/issues", "/-/issues")

    return (
        "{0}://{1}{2}/{{0}}".format(
            parsed.scheme, parsed.hostname, web_url_path,
        ),
        "{0}://{1}{2}/{{0}}".format(
            parsed.scheme, parsed.hostname, alt_web_url_path,
        ),
    )
