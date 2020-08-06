# -*- coding: utf-8 -*-

from datetime import datetime

import factory

from tests.helpers.gitlab import gl_format_datetime
from tests.test_users.factories.gitlab import GlUserFactory


class GlNoteFactory(factory.DictFactory):
    """Gitlab note factory."""

    id = factory.Faker("random_int")  # noqa: WPS125, A003
    body = factory.Faker("word")
    created_at = gl_format_datetime(datetime.now())
    updated_at = gl_format_datetime(datetime.now())
    author = factory.SubFactory(GlUserFactory)
