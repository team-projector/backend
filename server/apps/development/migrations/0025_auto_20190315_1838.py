# -*- coding: utf-8 -*-

# Generated by Django 2.1.7 on 2019-03-15 15:38

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('development', '0024_auto_20190314_1749'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='note',
            options={'ordering': ('-created_at',), 'verbose_name': 'VN__NOTE', 'verbose_name_plural': 'VN__NOTES'},
        ),
    ]
