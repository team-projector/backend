# -*- coding: utf-8 -*-

# Generated by Django 2.1.4 on 2018-12-10 13:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("development", "0005_auto_20181209_1947"),
    ]

    operations = [
        migrations.AddField(
            model_name="issue",
            name="created_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
