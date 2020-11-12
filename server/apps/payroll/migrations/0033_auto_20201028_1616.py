# Generated by Django 3.1.2 on 2020-10-28 13:16

import apps.payroll.models.work_break
from django.db import migrations
import jnt_django_toolbox.models.fields.enum


class Migration(migrations.Migration):

    dependencies = [
        ('payroll', '0032_auto_20201020_1439'),
    ]

    operations = [
        migrations.AlterField(
            model_name='workbreak',
            name='reason',
            field=jnt_django_toolbox.models.fields.enum.EnumField(choices=[('DAYOFF', 'CH__DAYOFF'), ('VACATION', 'CH__VACATION'), ('DISEASE', 'CH__DISEASE')], enum=apps.payroll.models.work_break.WorkBreakReason, help_text='HT__REASON', verbose_name='VN__REASON'),
        ),
    ]