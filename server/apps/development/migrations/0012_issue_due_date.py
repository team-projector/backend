# Generated by Django 2.1.5 on 2019-01-16 15:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('development', '0011_auto_20190114_2149'),
    ]

    operations = [
        migrations.AddField(
            model_name='issue',
            name='due_date',
            field=models.DateField(blank=True, null=True),
        ),
    ]
