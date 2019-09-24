# -*- coding: utf-8 -*-

import graphene


class ProjectIssuesSummary(graphene.ObjectType):
    opened_count = graphene.Int()
    percentage = graphene.Float()
    remains = graphene.Int()
