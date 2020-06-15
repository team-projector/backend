# -*- coding: utf-8 -*-

# Generated by Django 2.2.1 on 2019-06-07 13:07

import jnt_django_toolbox.models.fields
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("development", "0050_auto_20190530_1752"),
    ]

    operations = [
        migrations.AlterField(
            model_name="issue",
            name="feature",
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="issues", to="development.Feature"),
        ),
        migrations.AlterField(
            model_name="mergerequest",
            name="assignee",
            field=models.ForeignKey(blank=True, help_text="HT__ASSIGNEE", null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="assignee_merge_requests", to=settings.AUTH_USER_MODEL, verbose_name="VN__ASSIGNEE"),
        ),
        migrations.AlterField(
            model_name="mergerequest",
            name="author",
            field=models.ForeignKey(blank=True, help_text="HT__AUTHOR", null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="author_merge_requests", to=settings.AUTH_USER_MODEL, verbose_name="VN__AUTHOR"),
        ),
        migrations.AlterField(
            model_name="projectmember",
            name="role",
            field=models.CharField(choices=[("developer", "CH_DEVELOPER"), ("project_manager", "CH_PM"), ("customer", "CH_CUSTOMER")], help_text="HT__ROLE", max_length=20, verbose_name="VN__ROLE"),
        ),
        migrations.AlterField(
            model_name="teammember",
            name="roles",
            field=jnt_django_toolbox.models.fields.BitField((("leader", "CH_LEADER"), ("developer", "CH_DEVELOPER")), default=0),
        ),
    ]
