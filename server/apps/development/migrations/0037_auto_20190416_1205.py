# -*- coding: utf-8 -*-

# Generated by Django 2.2 on 2019-04-16 09:05

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('development', '0036_auto_20190416_1159'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='projectmember',
            options={'verbose_name': 'VN__PROJECT_MEMBER', 'verbose_name_plural': 'VN__PROJECT_MEMBERS'},
        ),
        migrations.AlterUniqueTogether(
            name='projectmember',
            unique_together={('user', 'role', 'object_id')},
        ),
    ]
