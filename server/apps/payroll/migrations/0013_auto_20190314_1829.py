# -*- coding: utf-8 -*-

# Generated by Django 2.1.7 on 2019-03-14 15:29

from django.db import migrations

import apps.core.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ("payroll", "0012_spenttime"),
    ]

    operations = [
        migrations.AlterField(
            model_name="payroll",
            name="sum",
            field=apps.core.models.fields.MoneyField(decimal_places=2, default=0, help_text="HT__SUM", max_digits=14, verbose_name="VN__SUM"),
        ),
    ]
