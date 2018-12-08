# Generated by Django 2.1.4 on 2018-12-08 18:31

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('development', '0003_auto_20181208_1715'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='issue',
            name='time_spend',
        ),
        migrations.AddField(
            model_name='issue',
            name='labels',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(blank=True, max_length=255), blank=True, help_text='HT__LABELS', null=True, size=None, verbose_name='VN__LABELS'),
        ),
        migrations.AddField(
            model_name='issue',
            name='state',
            field=models.CharField(blank=True, help_text='HT__STATE', max_length=255, null=True, verbose_name='VN__STATE'),
        ),
        migrations.AddField(
            model_name='issue',
            name='total_time_spent',
            field=models.PositiveIntegerField(help_text='HT__TOTAL_TIME_SPENT', null=True, verbose_name='VN__TOTAL_TIME_SPENT'),
        ),
    ]
