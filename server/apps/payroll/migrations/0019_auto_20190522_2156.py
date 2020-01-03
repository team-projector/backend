# -*- coding: utf-8 -*-

# Generated by Django 2.2.1 on 2019-05-22 18:56

from django.db import migrations, models

import apps.core.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ("payroll", "0018_workbreak"),
    ]

    operations = [
        migrations.AddField(
            model_name="spenttime",
            name="customer_rate",
            field=models.FloatField(help_text="HT__CUSTOMER_RATE", null=True, verbose_name="VN__CUSTOMER_RATE"),
        ),
        migrations.AddField(
            model_name="spenttime",
            name="customer_sum",
            field=apps.core.models.fields.MoneyField(decimal_places=2, default=0, help_text="HT__CUSTOMER_SUM", max_digits=14, verbose_name="VN__CUSTOMER_SUM"),
        ),
    ]
