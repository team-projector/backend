# Generated by Django 3.1.4 on 2020-12-24 15:44

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('skills', '0005_auto_20201112_1257'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='position',
            options={'ordering': ('title',), 'verbose_name': 'VN__POSITION', 'verbose_name_plural': 'VN__POSITIONS'},
        ),
        migrations.AlterModelOptions(
            name='skill',
            options={'ordering': ('title',), 'verbose_name': 'VN__SKILL', 'verbose_name_plural': 'VN__SKILLS'},
        ),
        migrations.AlterModelOptions(
            name='skillgroup',
            options={'ordering': ('title',), 'verbose_name': 'VN__SKILL_GROUP', 'verbose_name_plural': 'VN__SKILL_GROUPS'},
        ),
        migrations.AlterModelOptions(
            name='userskilllevel',
            options={'ordering': ('user__login',), 'verbose_name': 'VN__USER_SKILL_LEVEL', 'verbose_name_plural': 'VN__USER_SKILL_LEVELS'},
        ),
    ]
