# Generated by Django 3.1.4 on 2020-12-24 15:44

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0030_delete_position'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='token',
            options={'ordering': ('-created',), 'verbose_name': 'VN__TOKEN', 'verbose_name_plural': 'VN__TOKENS'},
        ),
    ]