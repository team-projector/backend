from rest_framework import serializers


class FakeSerializer(serializers.Serializer):
    pass


class LinkSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    presentation = serializers.SerializerMethodField()

    @staticmethod
    def get_presentation(instance):
        return str(instance)

    class Meta:
        fields = ('id', 'presentation')
