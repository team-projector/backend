# Generated by Django 3.0.3 on 2020-02-14 13:32

from django.db import migrations

from apps.development.models.ticket import TicketType


def set_ticket_default_type(apps, schema_editor):
    Ticket = apps.get_model('development', 'Ticket')
    Ticket.objects.filter(type='').update(type=TicketType.FEATURE)


class Migration(migrations.Migration):
    dependencies = [
        ('development', '0071_auto_20200213_1808'),
    ]

    operations = [
        migrations.RunPython(set_ticket_default_type),
    ]
