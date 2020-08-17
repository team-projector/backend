# -*- coding: utf-8 -*-

import pytest
from jnt_django_toolbox.helpers.objects import dict2obj

from apps.development.models.note import NoteType
from apps.development.services.note.gitlab import CommentParser
from tests.test_development.factories import IssueFactory
from tests.test_development.factories.gitlab import GlNoteFactory

comment_parser = CommentParser()


@pytest.fixture()
def issue(db):
    """
    Issue.

    :param db:
    """
    return IssueFactory.create(
        gl_url="https://gitlab.com/junte/esanum/social/backend/issues/0",
    )


@pytest.mark.parametrize(
    "body",
    ["", "any string", "#4534p", "e#4534", "https://gitlab.com/issue/3510"],
)
def test_empty(body, issue):
    """
    Test empty.

    :param body:
    :param issue:
    """
    gl_note = GlNoteFactory.create(body=body)

    assert comment_parser.parse(dict2obj(gl_note), issue) is None


def test_links(issue):
    """
    Test links.

    :param issue:
    """
    link = "https://gitlab.com/junte/esanum/social/backend/-/issues/3510"
    gl_note = GlNoteFactory.create(body="issue {0}".format(link))
    note_type, note_data = comment_parser.parse(dict2obj(gl_note), issue)

    assert note_type == NoteType.COMMENT
    assert note_data.get("issues") == [link]
    assert note_data.get("numbers") is None


def test_tickets(issue):
    """
    Test tickets.

    :param issue:
    """
    gl_note = GlNoteFactory.create(
        body="tickets {0}, {1}, {2}".format(
            "https://teamprojector.com/en/manager/milestones/40525;ticket=439",
            "https://teamprojector.com/en/manager/milestones/40521;ticket=345;type=testing",  # noqa: E501
            "https://teamprojector.com/en/manager/milestones/40521;ticket=439;type=testing",  # noqa: E501
        ),
    )
    note_type, note_data = comment_parser.parse(dict2obj(gl_note), issue)

    tickets = note_data.get("tickets")

    assert note_type == NoteType.COMMENT
    assert len(tickets) == 2
    assert set(tickets) == {"439", "345"}


def test_numbers(issue):
    """
    Test numbers.

    :param issue:
    """
    gl_note = GlNoteFactory.create(body="issue #3511")
    note_type, note_data = comment_parser.parse(dict2obj(gl_note), issue)

    links = note_data.get("issues")

    assert note_type == NoteType.COMMENT
    assert links == [
        "https://gitlab.com/junte/esanum/social/backend/issues/3511",
    ]


def test_links_numbers(issue):
    """
    Test links numbers.

    :param issue:
    """
    link = "https://gitlab.com/junte/esanum/social/backend/-/issues/100"
    gl_note = GlNoteFactory.create(body="issue #3510 links {0}".format(link))
    note_type, note_data = comment_parser.parse(dict2obj(gl_note), issue)

    links = note_data.get("issues")

    assert note_type == NoteType.COMMENT
    assert len(links) == 2
    assert set(links) == {
        link,
        "https://gitlab.com/junte/esanum/social/backend/issues/3510",
    }
