# -*- coding: utf-8 -*-

from django.db import transaction


def trigger_on_commit():
    """Force on commit actions."""
    connection = transaction.get_connection()

    current_run_on_commit = connection.run_on_commit
    connection.run_on_commit = []
    while current_run_on_commit:
        sids, func = current_run_on_commit.pop(0)
        func()
