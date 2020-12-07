def assert_instance_fields(instance, **kwargs) -> None:
    """Check instance fields values."""
    for attr, attr_value in kwargs.items():
        assert getattr(instance, attr) == attr_value
