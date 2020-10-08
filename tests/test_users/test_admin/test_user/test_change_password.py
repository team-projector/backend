def test_change_password_link(user, user_admin):
    """Test change password link."""
    link = user_admin.change_password_link(user)

    assert link == (
        '<a href="/admin/users/user/{0}/password/">change password</a>'
    ).format(user.pk)
