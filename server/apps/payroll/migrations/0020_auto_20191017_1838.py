# Generated by Django 2.2.5 on 2019-10-17 15:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payroll', '0019_auto_20190522_2156'),
    ]

    operations = [
        migrations.AlterField(
            model_name='salary',
            name='comments',
            field=models.TextField(blank=True, default='', help_text='HT__COMMENTS', verbose_name='VN__COMMENTS'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='workbreak',
            name='decline_reason',
            field=models.TextField(blank=True, default='', help_text='HT__DECLINE_REASON', verbose_name='VN__DECLINE_REASON'),
            preserve_default=False,
        ),
    ]
