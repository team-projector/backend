# -*- coding: utf-8 -*-

# Generated by Django 2.2 on 2019-05-21 08:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0012_auto_20190317_2026'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='daily_work_hours',
            field=models.PositiveIntegerField(default=8),
        ),
    ]
