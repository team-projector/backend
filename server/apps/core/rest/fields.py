from rest_framework import serializers


class IntegerListField(serializers.ListField):
    child = serializers.IntegerField()
