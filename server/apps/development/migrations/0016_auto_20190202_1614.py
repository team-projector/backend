# -*- coding: utf-8 -*-

# Generated by Django 2.1.5 on 2019-02-02 13:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("development", "0015_auto_20190129_1147"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="label",
            options={"verbose_name": "VN__LABEL", "verbose_name_plural": "VN__LABELS"},
        ),
        migrations.AlterModelOptions(
            name="note",
            options={"ordering": ("-created_at",), "verbose_name": "VN__NOTE", "verbose_name_plural": "VN__NOTES"},
        ),
        migrations.AddField(
            model_name="note",
            name="body",
            field=models.TextField(null=True),
        ),
    ]
