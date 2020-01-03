# -*- coding: utf-8 -*-

# Generated by Django 2.2 on 2019-04-16 08:59

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("contenttypes", "0002_remove_content_type_name"),
        ("development", "0035_projectgroup_members"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="project",
            name="members",
        ),
        migrations.RemoveField(
            model_name="projectgroup",
            name="members",
        ),
        migrations.AddField(
            model_name="projectmember",
            name="content_type",
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to="contenttypes.ContentType"),
        ),
        migrations.AddField(
            model_name="projectmember",
            name="object_id",
            field=models.PositiveIntegerField(null=True),
        ),
    ]
