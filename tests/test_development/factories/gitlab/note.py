# -*- coding: utf-8 -*-

from datetime import datetime

import factory

from tests.helpers.gitlab import gl_format_datetime
from tests.test_users.factories.gitlab import GlUserFactory


class GlNoteFactory(factory.DictFactory):
    id = factory.Faker("random_int")
    body = factory.Faker("word")
    created_at = gl_format_datetime(datetime.now())
    updated_at = gl_format_datetime(datetime.now())
    author = factory.SubFactory(GlUserFactory)
