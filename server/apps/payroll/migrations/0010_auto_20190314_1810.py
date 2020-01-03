# -*- coding: utf-8 -*-

# Generated by Django 2.1.7 on 2019-03-14 15:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("payroll", "0009_auto_20190314_1759"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="bonus",
            options={"ordering": ("-created_at",), "verbose_name": "VN__BONUS", "verbose_name_plural": "VN__BONUSES"},
        ),
        migrations.AlterModelOptions(
            name="payment",
            options={"ordering": ("-created_at",), "verbose_name": "VN__PAYMENT", "verbose_name_plural": "VN__PAYMENTS"},
        ),
        migrations.AlterModelOptions(
            name="payroll",
            options={"ordering": ("-created_at",), "verbose_name": "VN__PAYROLL", "verbose_name_plural": "VN__PAYROLLS"},
        ),
        migrations.AlterModelOptions(
            name="penalty",
            options={"ordering": ("-created_at",), "verbose_name": "VN__PENALTY", "verbose_name_plural": "VN__PENALTIES"},
        ),
        migrations.AlterModelOptions(
            name="spenttime",
            options={"ordering": ("-date",), "verbose_name": "VN__SPENT_TIME", "verbose_name_plural": "VN__SPENT_TIMES"},
        ),
        migrations.AddField(
            model_name="spenttime",
            name="rate",
            field=models.FloatField(help_text="HT__RATE", null=True, verbose_name="VN__RATE"),
        ),
    ]
