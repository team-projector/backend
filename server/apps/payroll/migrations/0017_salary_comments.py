# -*- coding: utf-8 -*-

# Generated by Django 2.1.7 on 2019-03-19 14:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("payroll", "0016_auto_20190317_1920"),
    ]

    operations = [
        migrations.AddField(
            model_name="salary",
            name="comments",
            field=models.TextField(blank=True, help_text="HT__COMMENTS", null=True, verbose_name="VN__COMMENTS"),
        ),
    ]
