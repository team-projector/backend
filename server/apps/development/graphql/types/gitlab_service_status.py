# -*- coding: utf-8 -*-

import graphene


class GitlabServiceStatusType(graphene.ObjectType):
    """
    A class representing gitlab service status fields.
    """
    name = graphene.String()
    time = graphene.DateTime()
