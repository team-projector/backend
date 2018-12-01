from django import forms
from django.conf import settings

DEFAULT_PERMISSIONS = ['add', 'change', 'delete']


class PermissionSelectMultipleWidget(forms.CheckboxSelectMultiple):
    template_name = 'users/widgets/permissions.html'
    custom_permission_types = []
    groups_permissions = []

    def get_context(self, name, value, attrs):
        if value is None:
            value = []

        return {
            'name': name,
            'value': value,
            'table': self.get_table(),
            'groups_permissions': self.groups_permissions,
            'default_permission_types': DEFAULT_PERMISSIONS,
            'custom_permission_types': self.custom_permission_types
        }

    def get_table(self):
        table = []
        row = None
        last_app = None
        last_model = None

        for permission in self.choices.queryset.select_related('content_type').all():
            # get permission type from codename
            codename = permission.codename
            model_part = '_' + permission.content_type.model
            permission_type = codename
            if permission_type.endswith(model_part):
                permission_type = permission_type[:-len(model_part)]

            # get app label and model verbose name
            #

            if f'apps.{permission.content_type.app_label}' not in settings.PROJECT_APPS:
                continue

            app = permission.content_type.app_label.replace('_', ' ')
            model_class = permission.content_type.model_class()
            model_verbose_name = model_class._meta.verbose_name if model_class else None

            if permission_type not in list(DEFAULT_PERMISSIONS) + self.custom_permission_types:
                self.custom_permission_types.append(permission_type)

            # each row represents one model with its permissions categorized by type
            is_app_or_model_different = last_model != model_class or last_app != app
            if is_app_or_model_different:
                row = dict(model=model_verbose_name, model_class=model_class, app=app, permissions={})

            row['permissions'][permission_type] = permission

            if is_app_or_model_different:
                table.append(row)

            last_app = app
            last_model = model_class

        return table

    class Media:
        css = {
            'all': ['users/css/widgets/permissions.css']
        }
