from django.core.management.base import BaseCommand

from apps.development.utils.loaders import check_projects_deleted_issues


class Command(BaseCommand):
    def handle(self, *args, **options):
        check_projects_deleted_issues()
