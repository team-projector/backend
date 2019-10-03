# -*- coding: utf-8 -*-

import graphene


class MergeRequestMetricsType(graphene.ObjectType):
    """
    A class representing merge requests metrics fields.
    """
    remains = graphene.Int()
    efficiency = graphene.Float()
    payroll = graphene.Float()
    paid = graphene.Float()
