# -*- coding: utf-8 -*-

# Generated by Django 2.1.5 on 2019-02-04 12:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("payroll", "0006_auto_20190204_1442"),
    ]

    operations = [
        migrations.AlterField(
            model_name="spenttime",
            name="date",
            field=models.DateField(null=True),
        ),
    ]
