# -*- coding: utf-8 -*-

# Generated by Django 2.2.4 on 2019-09-06 12:46

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('development', '0057_auto_20190806_0943'),
    ]

    operations = [
        migrations.CreateModel(
            name='Ticket',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('type', models.CharField(blank=True, choices=[('feature', 'CH_FEATURE'), ('improvement', 'CH_IMPROVEMENT'), ('bug_fixing', 'CH_BUG_FIXING')], help_text='HT__TYPE', max_length=50, null=True, verbose_name='VN__TYPE')),
                ('title', models.CharField(help_text='HT__TITLE', max_length=255, verbose_name='VN__TITLE')),
                ('start_date', models.DateField(blank=True, help_text='HT__START_DATE', null=True, verbose_name='VN__START_DATE')),
                ('due_date', models.DateField(blank=True, help_text='HT__DUE_DATE', null=True, verbose_name='VN__DUE_DATE')),
                ('url', models.URLField(blank=True, help_text='HT__URL', null=True, verbose_name='VN__URL')),
                ('milestone', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='ticket', to='development.Milestone')),
            ],
            options={
                'verbose_name': 'VN__TICKET',
                'verbose_name_plural': 'VN__TICKETS',
                'ordering': ('-created_at',),
            },
        ),
        migrations.RemoveField(
            model_name='issue',
            name='feature',
        ),
        migrations.DeleteModel(
            name='Feature',
        ),
        migrations.AddField(
            model_name='issue',
            name='ticket',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='issues', to='development.Ticket'),
        ),
    ]
