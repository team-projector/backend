# -*- coding: utf-8 -*-

# Generated by Django 2.1.7 on 2019-04-04 13:02

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("contenttypes", "0002_remove_content_type_name"),
        ("development", "0027_auto_20190404_1146"),
    ]

    operations = [
        migrations.AddField(
            model_name="issue",
            name="content_type",
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to="contenttypes.ContentType"),
        ),
        migrations.AddField(
            model_name="issue",
            name="object_id",
            field=models.PositiveIntegerField(null=True),
        ),
    ]
