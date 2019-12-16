# -*- coding: utf-8 -*-


# TODO think...
def check_user(user, gl_user):
    assert user.login == gl_user['username']
    assert user.email == gl_user['public_email']
    assert user.name == gl_user['name']
    assert user.gl_avatar == gl_user['avatar_url']
    assert user.gl_url == gl_user['web_url']
