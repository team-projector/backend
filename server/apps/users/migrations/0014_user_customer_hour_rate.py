# -*- coding: utf-8 -*-

# Generated by Django 2.2.1 on 2019-05-22 15:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0013_user_daily_work_hours"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="customer_hour_rate",
            field=models.FloatField(default=0, help_text="HT__CUSTOMER_HOUR_RATE", verbose_name="VN__CUSTOMER_HOUR_RATE"),
        ),
    ]
