# Generated by Django 2.1.7 on 2019-03-17 16:09

import apps.core.db.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('payroll', '0014_auto_20190315_1838'),
    ]

    operations = [
        migrations.AddField(
            model_name='salary',
            name='penalty',
            field=apps.core.db.fields.MoneyField(decimal_places=2, default=0, help_text='HT__PENALTY', max_digits=14, verbose_name='VN__PENALTY'),
        ),
    ]
