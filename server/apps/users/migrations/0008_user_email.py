# -*- coding: utf-8 -*-

# Generated by Django 2.1.5 on 2019-02-03 21:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0007_auto_20190202_1614"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="email",
            field=models.CharField(blank=True, help_text="HT__LOGIN", max_length=150, null=True, unique=True, verbose_name="VN__LOGIN"),
        ),
    ]
