from rest_framework import serializers


class LoginInput(serializers.Serializer):
    """Login mutation serializer."""

    login = serializers.CharField()
    password = serializers.CharField()
