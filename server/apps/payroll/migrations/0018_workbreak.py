# -*- coding: utf-8 -*-

# Generated by Django 2.2.1 on 2019-05-22 15:58

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('payroll', '0017_salary_comments'),
    ]

    operations = [
        migrations.CreateModel(
            name='WorkBreak',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('approve_state', models.CharField(choices=[('created', 'CH_CREATED'), ('approved', 'CH_APPROVED'), ('declined', 'CH_DECLINED')], default='created', help_text='HT__APPROVE_STATE', max_length=15, verbose_name='VN__APPROVE_STATE')),
                ('approved_at', models.DateTimeField(blank=True, help_text='HT__APPROVED_AT', null=True, verbose_name='VN__APPROVED_AT')),
                ('decline_reason', models.TextField(blank=True, help_text='HT__DECLINE_REASON', null=True, verbose_name='VN__DECLINE_REASON')),
                ('from_date', models.DateTimeField(help_text='HT__DATE_FROM', verbose_name='VN__DATE_FROM')),
                ('to_date', models.DateTimeField(help_text='HT__DATE_TO', verbose_name='VN__DATE_TO')),
                ('reason', models.CharField(choices=[('dayoff', 'CH_DAYOFF'), ('vacation', 'CH_VACATION'), ('disease', 'CH_DISEASES')], help_text='HT__REASON', max_length=15, verbose_name='VN__REASON')),
                ('comment', models.TextField(help_text='HT__COMMENT', verbose_name='VN__COMMENT')),
                ('approved_by', models.ForeignKey(blank=True, help_text='HT__APPROVED_BY', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='approve_break', to=settings.AUTH_USER_MODEL, verbose_name='VN__APPROVED_BY')),
                ('user', models.ForeignKey(help_text='HT__USER', on_delete=django.db.models.deletion.CASCADE, related_name='work_break', to=settings.AUTH_USER_MODEL, verbose_name='VN__USER')),
            ],
            options={
                'verbose_name': 'VN__WORKBREAK',
                'verbose_name_plural': 'VN__WORKBREAKS',
                'ordering': ('-from_date',),
            },
        ),
    ]
