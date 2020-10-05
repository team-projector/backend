# -*- coding: utf-8 -*-

from apps.development.models import Issue
from apps.development.services.issue.allowed import filter_allowed_for_user


def check_allowed_for_user(user, issues):
    """
    Check allowed for user.

    :param user:
    :param issues:
    """
    allowed = filter_allowed_for_user(Issue.objects.all(), user)

    assert allowed.count() == len(issues)
    assert set(allowed) == set(issues)
