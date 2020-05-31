# -*- coding: utf-8 -*-

import factory
from django.contrib.contenttypes.models import ContentType

from tests.test_development.factories.mixins.gl_field import GitlabFieldMixin
from tests.test_development.factories.project_group import ProjectGroupFactory


class MilestoneFactory(GitlabFieldMixin):
    class Meta:
        abstract = True
        exclude = ["content_object"]

    owner = factory.SubFactory(ProjectGroupFactory)
    object_id = factory.SelfAttribute("owner.id")
    content_type = factory.LazyAttribute(
        lambda instance: ContentType.objects.get_for_model(instance.owner),
    )
