# Generated by Django 3.0.4 on 2020-03-16 13:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0023_auto_20200305_1618'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='notify_pipeline_status',
            field=models.BooleanField(default=False, help_text='HT__NOTIFY_PIPELINE_STATUS', verbose_name='VN__NOTIFY_PIPELINE_STATUS'),
        ),
    ]
