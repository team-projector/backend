# Generated by Django 2.1.7 on 2019-03-14 14:49

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('development', '0023_auto_20190313_1820'),
    ]

    operations = [
        migrations.AlterField(
            model_name='issue',
            name='user',
            field=models.ForeignKey(blank=True, help_text='HT__USER', null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, verbose_name='VN__USER'),
        ),
        migrations.AlterField(
            model_name='teammember',
            name='user',
            field=models.ForeignKey(help_text='HT__USER', on_delete=django.db.models.deletion.CASCADE, related_name='team_members', to=settings.AUTH_USER_MODEL, verbose_name='VN__USER'),
        ),
    ]