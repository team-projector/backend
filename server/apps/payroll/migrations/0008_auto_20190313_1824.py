# -*- coding: utf-8 -*-

# Generated by Django 2.1.7 on 2019-03-13 15:24

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("payroll", "0007_auto_20190204_1557"),
    ]

    operations = [
        migrations.RenameField(
            model_name="spenttime",
            old_name="employee",
            new_name="user",
        )
    ]
