from pytest import raises

from apps.development.services.note.gitlab import BaseNoteParser


def test_base_parser():
    with raises(NotImplementedError):
        BaseNoteParser().parse(None)
