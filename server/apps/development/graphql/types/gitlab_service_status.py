# -*- coding: utf-8 -*-

import graphene


class GitlabServiceStatusType(graphene.ObjectType):
    """Gitlab service status type."""

    name = graphene.String()
    time = graphene.DateTime()
