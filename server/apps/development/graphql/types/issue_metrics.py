# -*- coding: utf-8 -*-

import graphene


class IssueMetricsType(graphene.ObjectType):
    """Issue metrics type."""

    remains = graphene.Int()
    efficiency = graphene.Float()
    payroll = graphene.Float()
    paid = graphene.Float()
