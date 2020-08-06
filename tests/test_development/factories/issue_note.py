# -*- coding: utf-8 -*-

import factory
import pytz

from apps.development.models import Note
from tests.test_development.factories.issue import IssueFactory


class IssueNoteFactory(factory.django.DjangoModelFactory):
    """Issue note factory."""

    class Meta:
        model = Note

    gl_id = factory.Sequence(lambda seq: seq)
    created_at = factory.Faker(
        "date_time_this_year",
        before_now=True,
        after_now=False,
        tzinfo=pytz.UTC,
    )
    content_object = factory.SubFactory(IssueFactory)
    data = {}  # noqa: WPS110
