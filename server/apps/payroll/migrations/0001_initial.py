# -*- coding: utf-8 -*-

# Generated by Django 2.1.4 on 2018-12-13 15:12

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("contenttypes", "0002_remove_content_type_name"),
    ]

    operations = [
        migrations.CreateModel(
            name="TimeSpend",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("time_spent", models.IntegerField(help_text="HT__TIME_SPENT", verbose_name="VN__TIME_SPENT")),
                ("object_id", models.PositiveIntegerField()),
                ("salary", models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ("content_type", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="contenttypes.ContentType")),
                ("employee", models.ForeignKey(help_text="HT__EMPLOYEE", on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name="VN__EMPLOYEE")),
            ],
            options={
                "verbose_name": "VN__TIME_SPEND",
                "verbose_name_plural": "VN__TIME_SPEND",
                "ordering": ("-created_at", "employee"),
            },
        ),
    ]
