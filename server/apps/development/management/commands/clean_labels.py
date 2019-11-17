# -*- coding: utf-8 -*-

import time

from django.conf import settings
from django.core.management.base import BaseCommand

from apps.development.services.project.gl.manager import (
    ProjectGlManager,
)
from apps.development.services.project_group.gl.manager import (
    ProjectGroupGlManager,
)

DELAY = .5  # sec


class Command(BaseCommand):
    group_for_sync = None
    only_log = False

    def _parse_params(self, *args, **options):
        self.group_for_sync = options.get('group')
        self.only_log = options.get('log')

    def add_arguments(self, parser):
        parser.add_argument(
            '-g',
            '--group',
            action='store',
            default=None,
            help='Gitlab group_id for sync labels'
        )
        parser.add_argument(
            '-l',
            '--log',
            action='store_true',
            default=False,
            help='Show only log, without apply'
        )

    def handle(self, *args, **options):
        self._parse_params(*args, **options)

        if not settings.GITLAB_NO_SYNC:
            print('GITLAB_NO_SYNC is False, available only mode log\n')
            self.only_log = True

        # self._prepare_data()
        self.start_sync()
        print('\nsync complete')

    def start_sync(self):
        if self.group_for_sync:
            self._sync_labels_for_group()
        else:
            self._start_sync(self.get_all_groups())

    def get_all_groups(self):
        group_manager = ProjectGroupGlManager()
        return group_manager.provider.get_gl_groups(all=True)

    def _start_sync(self, groups):
        root_groups = (group for group in groups if group.parent_id is None)

        for root_group in root_groups:
            self.sync_labels(
                root_group,
                self.get_all_subgroups(root_group, groups),
            )

    def sync_labels(self, root_group, subgroups, sync_root_projects=True):
        print(f'sync root groups {root_group.name}')

        project_manager = ProjectGlManager()
        root_group_labels = root_group.labels.list(all=True)

        print(f'root labels -> {",".join((l.name for l in root_group_labels))}')

        root_projects = root_group.projects.list(all=True)

        for subgroup in subgroups:
            print(
                f'\n  subgroup -> {subgroup.name} ({subgroup.web_url}/-/labels)')
            time.sleep(DELAY)

            projects = subgroup.projects.list(all=True)

            if sync_root_projects:
                projects.extend(root_projects)

            for project in projects:
                print(
                    f'    project -> {project.name} ({project.web_url}/-/labels)')

                gl_project = project_manager.project_provider.gl_client.projects.get(
                    project.id,
                )
                project_labels = gl_project.labels.list(all=True)

                print(
                    f'      project labels: {", ".join((l.name for l in project_labels))}')

                labels_for_rename = self.get_equal_labels(
                    root_group_labels,
                    project_labels,
                )

                updated_labels = self._rename_labels(
                    gl_project,
                    labels_for_rename,
                )
                labels_for_delete = [l.name for l in updated_labels]

                if self.only_log:
                    if labels_for_rename:
                        labels = {l.name for l in labels_for_rename}
                        issues = [p for p in
                                  gl_project.issues.list(all=True)
                                  if set(p.labels) & labels]
                        print(
                            f'        issues for update: {", ".join((self._get_issue_present(i) for i in issues))}')

                for updated_label in updated_labels:
                    lower_label = updated_label.name.strip('__')
                    root_label = [l for l in root_group_labels if
                                  l.name.lower() == lower_label][0]

                    self._update_issues(gl_project, updated_label.name,
                                        root_label.name)

                for project_label in gl_project.labels.list(all=True):
                    if project_label.name in labels_for_delete:
                        project_label.delete()

    def _get_issue_present(self, issue):
        labels = ', '.join(issue.labels)
        return f'#{issue.iid} [{labels}]'

    def _sync_labels_for_group(self):
        group_manager = ProjectGroupGlManager()
        gl_client = group_manager.provider.gl_client
        root_group = self._get_root_group_for_group(gl_client,
                                                    self.group_for_sync)
        group = gl_client.groups.get(id=self.group_for_sync)

        subgroups = [gl_client.groups.get(id=g.id) for g in
                     self.get_all_subgroups(group, self.get_all_groups())]

        subgroups.append(group)

        self.sync_labels(root_group, subgroups, sync_root_projects=False)

    def _update_issues(self, gl_project, old_label, label_for_add):
        issues = gl_project.issues.list(all=True, labels=[old_label])

        for issue_iid in {i.iid for i in issues if
                          label_for_add not in i.labels}:
            issue = gl_project.issues.get(issue_iid)
            issue.labels.append(label_for_add)
            issue.save()

    def _get_root_group_for_group(self, gl_client, group_id):
        if not group_id:
            raise Exception('group_id not filled')

        parent_id = group_id

        while parent_id:
            group = gl_client.groups.get(id=parent_id)
            parent_id = group.parent_id

        return group

    def get_equal_labels(self, root_labels, labels):
        root_names = [label.name.lower() for label in root_labels]
        root_ids = [label.id for label in root_labels]

        return [label for label in labels if
                label.name.lower() in root_names and label.id not in root_ids]

    def get_all_subgroups(self, root_group, groups):
        all_groups = []
        parent_id = root_group.id
        sb_groups = [g for g in groups if g.parent_id == parent_id]
        all_groups.extend(sb_groups)

        for sb_group in sb_groups:
            all_groups.extend(self.get_all_subgroups(sb_group, groups))

        return all_groups

    def _rename_labels(self, gl_project, labels):
        if labels:
            print(
                f'      labels for rename: \033[1;31;48m{", ".join((l.name for l in labels))}\033[0m')

        updated_labels = []

        for label in labels:
            new_name = '__{}__'.format(label.name.lower())

            updated_data = {
                'name': label.name,
                'new_name': new_name,
            }
            if not self.only_log:
                label.manager.update(None, updated_data)
                updated_labels.append(
                    [l for l in gl_project.labels.list(all=True) if
                     l.id == label.id][0]
                )
        return updated_labels

    def _prepare_data(self):
        group_manager = ProjectGroupGlManager()

        gl_client = group_manager.provider.gl_client

        main_group_data = {'name': 'main-root-group', 'path': 'main-root-group',
                           'description': 'Main root group'}
        subgroup_1_data = {'name': 'sub-group-1', 'path': 'sub-group-1',
                           'description': 'Subgroup 1'}
        subgroup_2_data = {'name': 'sub-group-2', 'path': 'sub-group-2',
                           'description': 'Subgroup 2'}
        subgroup_1_1_data = {'name': 'sub-group-1-1', 'path': 'sub-group-1-1',
                             'description': 'Subgroup 1-1'}

        project_root_data = {'name': 'main-root-project',
                             'path': 'main-root-project',
                             'description': 'Main root project'}
        project_sbgr_1_data = {'name': 'project-sbgr-1',
                               'path': 'project-sbgr-1',
                               'description': 'Project subgroup 1'}
        project_sbgr_2_data = {'name': 'project-sbgr-2',
                               'path': 'project-sbgr-2',
                               'description': 'Project subgroup 2'}
        project_sbgr_1_1_data = {'name': 'project-sbgr-1-1',
                                 'path': 'project-sbgr-1-1',
                                 'description': 'Project subgroup 1-1'}

        main_group = self._get_or_create_group(gl_client, None, main_group_data)

        subgroup_1 = self._get_or_create_group(gl_client, main_group,
                                               subgroup_1_data)
        subgroup_2 = self._get_or_create_group(gl_client, main_group,
                                               subgroup_2_data)
        subgroup_1_1 = self._get_or_create_group(gl_client, subgroup_1,
                                                 subgroup_1_1_data)

        project_root = self._get_or_create_project(gl_client, main_group,
                                                   project_root_data)
        project_sbgr_1 = self._get_or_create_project(gl_client, subgroup_1,
                                                     project_sbgr_1_data)
        project_sbgr_2 = self._get_or_create_project(gl_client, subgroup_2,
                                                     project_sbgr_2_data)
        project_sbgr_1_1 = self._get_or_create_project(gl_client, subgroup_1_1,
                                                       project_sbgr_1_1_data)

        label_name = 'for_test'

        label_data_1 = {'name': label_name, 'color': '#1199aa',
                        'description': 'Main group label'}
        label_data_2 = {'name': label_name, 'color': '#2288bb',
                        'description': 'Subgroup 1'}
        label_data_3 = {'name': label_name, 'color': '#3377cc',
                        'description': 'Subgroup 2'}
        label_data_4 = {'name': label_name, 'color': '#4466dd',
                        'description': 'Subgroup 1-1'}
        label_data_5 = {'name': label_name, 'color': '#5555ee',
                        'description': 'Project root'}
        label_data_6 = {'name': label_name, 'color': '#6644ff',
                        'description': 'Project subgroup 1'}
        label_data_7 = {'name': label_name, 'color': '#7733ab',
                        'description': 'Project subgroup 2'}
        label_data_8 = {'name': label_name, 'color': '#8822cd',
                        'description': 'Project subgroup 1-1'}

        self._add_label_to_instance(project_sbgr_1_1, label_data_8)
        self._add_label_to_instance(project_sbgr_2, label_data_7)
        self._add_label_to_instance(project_sbgr_1, label_data_6)
        self._add_label_to_instance(project_root, label_data_5)
        self._add_label_to_instance(subgroup_1_1, label_data_4)
        self._add_label_to_instance(subgroup_2, label_data_3)
        self._add_label_to_instance(subgroup_1, label_data_2)
        self._add_label_to_instance(main_group, label_data_1)

        issue_data_1 = {'title': 'Issue title 1', 'description': 'Issues 1'}
        issue_data_2 = {'title': 'Issue title 2', 'description': 'Issues 2'}

        self._add_issue(project_sbgr_1_1, issue_data_1)
        self._add_issue(project_root, issue_data_2)

    def _get_or_create_group(self, gl_client, root_group, data):
        if not root_group:
            for gr in gl_client.groups.list(all=True):
                if gr.name == data['name']:
                    return gl_client.groups.get(gr.id)

            return gl_client.groups.create(data)

        for sbgroup in root_group.subgroups.list(all=True):
            if sbgroup.name == data['name']:
                return gl_client.groups.get(sbgroup.id)

        data['parent_id'] = root_group.id

        return gl_client.groups.create(data)

    def _get_or_create_project(self, gl_client, group, data):
        for project in group.projects.list(all=True):
            if project.name == data['name']:
                return gl_client.projects.get(id=project.id)

        data['namespace_id'] = group.id

        return gl_client.projects.create(data)

    def _add_label_to_instance(self, instance, data):
        labels = instance.labels.list(all=True)
        label_names = [l.name for l in labels]

        if data['name'] in label_names:
            return

        new_name = '__{}__'.format(data['name'])

        if new_name in label_names:
            label = [l for l in labels if l.name == new_name]

            updated_data = {
                'name': new_name,
                'new_name': new_name.strip('__'),
            }

            label.manager.update(None, updated_data)
            return

        instance.labels.create(data)

    def _add_issue(self, project, issue_data):
        issue_titles = [i.title for i in project.issues.list(all=True)]

        if issue_data['title'] not in issue_titles:
            project.issues.create(issue_data)
