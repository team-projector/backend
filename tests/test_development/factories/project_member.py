# -*- coding: utf-8 -*-

import factory

from apps.development.models import ProjectMember
from tests.test_users.factories.user import UserFactory


class ProjectMemberFactory(factory.django.DjangoModelFactory):
    """Project member factory."""

    class Meta:
        model = ProjectMember

    user = factory.SubFactory(UserFactory)
