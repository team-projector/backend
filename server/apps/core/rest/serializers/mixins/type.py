from rest_framework import serializers


class TypeSerializerMixin(serializers.ModelSerializer):
    __type__ = serializers.SerializerMethodField(
        read_only=True,
        method_name='get_type'
    )

    def get_type(self, instance):
        return self.Meta.model._meta.model_name

    def get_field_names(self, declared_fields, info):
        field_names = super().get_field_names(declared_fields, info)
        return ('__type__',) + tuple(field_names)
