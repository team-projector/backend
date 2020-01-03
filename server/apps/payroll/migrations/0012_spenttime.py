# -*- coding: utf-8 -*-

# Generated by Django 2.1.7 on 2019-03-14 15:27

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("contenttypes", "0002_remove_content_type_name"),
        ("development", "0024_auto_20190314_1749"),
        ("payroll", "0011_auto_20190314_1826"),
    ]

    operations = [
        migrations.CreateModel(
            name="SpentTime",
            fields=[
                ("payroll_ptr", models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to="payroll.Payroll")),
                ("date", models.DateField(null=True)),
                ("rate", models.FloatField(help_text="HT__RATE", null=True, verbose_name="VN__RATE")),
                ("time_spent", models.IntegerField(help_text="HT__TIME_SPENT", verbose_name="VN__TIME_SPENT")),
                ("object_id", models.PositiveIntegerField()),
                ("content_type", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="contenttypes.ContentType")),
                ("note", models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="time_spend", to="development.Note")),
            ],
            options={
                "verbose_name": "VN__SPENT_TIME",
                "verbose_name_plural": "VN__SPENT_TIMES",
                "ordering": ("-date",),
            },
            bases=("payroll.payroll",),
        ),
    ]
