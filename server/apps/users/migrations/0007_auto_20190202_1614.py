# -*- coding: utf-8 -*-

# Generated by Django 2.1.5 on 2019-02-02 13:14

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0006_user_name'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='user',
            options={'ordering': ('login',), 'verbose_name': 'VN__USER', 'verbose_name_plural': 'VN__USERS'},
        ),
    ]
