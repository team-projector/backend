from django.db import migrations

from apps.development.models.project_member import ProjectMemberRole


def fill_project_member_roles(apps, schema_editor):
    ProjectMember = apps.get_model("development", "ProjectMember")
    roles_map = _get_roles_map(ProjectMember)

    for role, bit_value in roles_map.items():
        ProjectMember.objects.filter(role=role).update(roles=bit_value)


def _get_roles_map(ProjectMember):
    return {
        ProjectMemberRole.MANAGER: ProjectMember.roles.MANAGER,
        ProjectMemberRole.DEVELOPER: ProjectMember.roles.DEVELOPER,
        ProjectMemberRole.CUSTOMER: ProjectMember.roles.CUSTOMER,
    }


class Migration(migrations.Migration):

    dependencies = [
        ('development', '0091_projectmember_roles'),
    ]

    operations = [
        migrations.RunPython(fill_project_member_roles),
    ]
