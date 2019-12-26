# -*- coding: utf-8 -*-


def register_user(mocker, user):
    mocker.register_get('/users/{0}'.format(
        user['id'],
    ), user)
