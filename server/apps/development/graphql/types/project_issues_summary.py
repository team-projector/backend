# -*- coding: utf-8 -*-

import graphene


class ProjectIssuesSummary(graphene.ObjectType):
    """
    A class representing project issue fields.
    """
    opened_count = graphene.Int()
    percentage = graphene.Float()
    remains = graphene.Int()
