def register_user(mocker, user):
    """Mock user retrive gitlab endpoint."""
    mocker.register_get("/users/{0}".format(user["id"]), user)
