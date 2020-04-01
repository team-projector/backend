# -*- coding: utf-8 -*-

import pytest

from apps.core.utils.objects import dict2obj
from apps.development.models.note import NoteType
from apps.development.services.note.gitlab import CommentParser
from tests.test_development.factories.gitlab import GlNoteFactory

comment_parser = CommentParser()


@pytest.mark.parametrize(
    "body",
    ["", "any string", "#4534p", "e#4534", "https://gitlab.com/issue/3510"],
)
def test_empty(body):
    gl_note = GlNoteFactory.create(body=body)

    assert comment_parser.parse(dict2obj(gl_note)) is None


def test_links():
    link = "https://gitlab.com/junte/esanum/social/backend/-/issues/3510"
    gl_note = GlNoteFactory.create(body="issue {0}".format(link))
    note_type, note_data = comment_parser.parse(dict2obj(gl_note))

    links = note_data.get("links")

    assert note_type == NoteType.COMMENT
    assert len(links) == 1
    assert links[0] == link
    assert note_data.get("numbers") is None


def test_numbers():
    gl_note = GlNoteFactory.create(body="issue #3511")
    note_type, note_data = comment_parser.parse(dict2obj(gl_note))

    numbers = note_data.get("numbers")

    assert note_type == NoteType.COMMENT
    assert len(numbers) == 1
    assert numbers[0] == "3511"
    assert note_data.get("links") is None


def test_links_numbers():
    link = "https://gitlab.com/junte/esanum/social/backend/-/issues/3510"
    gl_note = GlNoteFactory.create(body="issue #3510 links {0}".format(link))
    note_type, note_data = comment_parser.parse(dict2obj(gl_note))

    numbers = note_data.get("numbers")
    links = note_data.get("links")

    assert note_type == NoteType.COMMENT
    assert len(numbers) == 1
    assert len(links) == 1
    assert numbers[0] == "3510"
    assert links[0] == link
