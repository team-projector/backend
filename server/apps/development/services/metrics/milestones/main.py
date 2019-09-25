# -*- coding: utf-8 -*-

from apps.development.models import Milestone

from .provider import MilestoneMetrics, MilestoneMetricsProvider


def get_milestone_metrics(milestone: Milestone) -> MilestoneMetrics:
    return MilestoneMetricsProvider(milestone).get_metrics()
