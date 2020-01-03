# -*- coding: utf-8 -*-

# Generated by Django 2.1.5 on 2019-02-04 10:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0008_user_email"),
    ]

    operations = [
        migrations.AlterField(
            model_name="user",
            name="email",
            field=models.EmailField(blank=True, help_text="HT__LOGIN", max_length=150, null=True, unique=True, verbose_name="VN__LOGIN"),
        ),
    ]
