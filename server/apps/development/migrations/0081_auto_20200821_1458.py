# Generated by Django 3.1 on 2020-08-21 11:58

import django.core.serializers.json
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('development', '0080_auto_20200331_1929'),
    ]

    operations = [
        migrations.AlterField(
            model_name='note',
            name='data',
            field=models.JSONField(encoder=django.core.serializers.json.DjangoJSONEncoder),
        ),
    ]
