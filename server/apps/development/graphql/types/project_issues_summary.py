# -*- coding: utf-8 -*-

import graphene


class ProjectIssuesSummary(graphene.ObjectType):
    """
    Project issues summary type.
    """
    opened_count = graphene.Int()
    percentage = graphene.Float()
    remains = graphene.Int()
