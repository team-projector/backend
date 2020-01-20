# -*- coding: utf-8 -*-

from apps.development.models import Issue


def check_allowed_for_user(user, issues):
    allowed = Issue.objects.allowed_for_user(user)

    assert allowed.count() == len(issues)
    assert set(allowed) == set(issues)
