# Generated by Django 3.1.2 on 2020-10-20 11:39

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('payroll', '0032_auto_20201020_1439'),
        ('users', '0029_auto_20201020_1413'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Position',
        ),
    ]
