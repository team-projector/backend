# Generated by Django 2.2.2 on 2019-07-19 11:43

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('development', '0054_auto_20190627_1901'),
    ]

    operations = [
        migrations.RenameField(
            model_name='mergerequest',
            old_name='assignee',
            new_name='user',
        )
    ]
