# -*- coding: utf-8 -*-

import logging
from collections import namedtuple
from typing import Dict, List, Set, Union

from gitlab import GitlabDeleteError, GitlabUpdateError
from gitlab.v4.objects import Group as GitlabGroup
from gitlab.v4.objects import GroupLabelManager
from gitlab.v4.objects import Project as GitlabProject
from gitlab.v4.objects import ProjectLabelManager

from apps.core.gitlab.client import get_default_gitlab_client

logger = logging.getLogger(__name__)

Label = namedtuple('Label', ['id', 'name'])


class Project:
    """Represents a gitlab project with information about parent group."""

    def __init__(self, gl_api_object, parent, client) -> None:
        """Inits Project with gl_api_object, parent and client."""
        self._client = client
        self.labels: Dict[int, Label] = {}
        self.gl_api_object = gl_api_object
        self.parent = parent
        self.initial_labels = get_labels(gl_api_object)

    def adjust_nested_labels(self) -> None:
        """
        Adjusts labels in every issue and merge_request of the project.

        After renaming redundant labels:
        "to do" => "__23232212__1"
        this adds to the issues or merge requests having "__23232212__1" label
        original parent label with id=23232212, so after running this the issue
        with labels ["__23232212__1"] will have ["__23232212__1", "To Do"]
        """
        for attr_name in 'issues', 'mergerequests':
            manager = getattr(self.gl_api_object, attr_name)
            for gl_api_obj in manager.list(all=True):
                initial = sorted(gl_api_obj.labels)
                gl_api_obj.labels = list({
                    self._replace_label_by_id(l_name)
                    for l_name
                    in gl_api_obj.labels
                })

                if initial != gl_api_obj.labels:
                    gl_api_obj.save()

    def _replace_label_by_id(self, label_name) -> str:
        splitted = label_name.split('__')
        if len(label_name.split('__')) != 3:
            return label_name

        if not splitted[1].isnumeric():
            return label_name

        label_id = int(splitted[1])
        label = self.labels.get(label_id)
        return label.name if label else label_name


class Group:
    """Represents a gitlab group with information about parent group."""

    def __init__(
        self,
        gl_api_object,
        client,
        parent=None,
        dry_run=True,
    ) -> None:
        """Inits Group with gl_api_object, parent and client."""
        self._client = client
        self._dry_run = dry_run
        self.labels: Dict[int, Label] = {}
        self.gl_api_object = gl_api_object
        self.parent = parent
        self.projects = self._get_projects()
        self.subgroups = self._get_subgroups_for_group()
        self.initial_labels = get_labels(gl_api_object)

    def adjust_projects_nested_labels(self) -> None:
        """This runs adjust_nested_labels() for all projects in group."""
        for project in self.projects:
            project.adjust_nested_labels()

        for subgroup in self.subgroups:
            subgroup.adjust_projects_nested_labels()

    def _get_subgroups_for_group(self) -> List['Group']:
        ret = []

        subgroups = self.gl_api_object.subgroups.list(all=True)
        for gl_subgroup in subgroups:
            api_obj_group = self._client.groups.get(gl_subgroup.get_id())
            group = Group(
                gl_api_object=api_obj_group,
                client=self._client,
                parent=self,
                dry_run=self._dry_run,
            )
            ret.append(group)

        return ret

    def _get_projects(self) -> List[Project]:
        ret = []

        for gl_project in self.gl_api_object.projects.list(all=True):
            gl_api_object = self._client.projects.get(gl_project.get_id())
            project = Project(
                gl_api_object=gl_api_object,
                parent=self,
                client=self._client,
            )

            ret.append(project)

        return ret


def get_label_match(label_list: List[Label], matching_label: Label):
    """Having matching_label we look for the first match in label_list."""
    for label in label_list:
        match_by_name = label.name.lower() == matching_label.name.lower()

        if match_by_name and label.id != matching_label.id:
            return label


def get_labels(
    gl_api_object: Union[GitlabProject, GitlabGroup],
):
    """Gets all labels for group or project and returns them as Label object."""
    ret = {}
    labels = gl_api_object.labels.list(
        all=True,
    )

    for gl_label in labels:
        label_id = gl_label.attributes.get('id')
        label_name = gl_label.attributes.get('name')

        ret[label_id] = Label(
            id=label_id,
            name=label_name,
        )

    return ret


class LabelsCleaner:
    """Removes redundant labels which have similar names from group."""

    def __init__(self, client=None):
        """Inits LabelsCleaner with gitlab client."""
        if not client:
            client = get_default_gitlab_client()
        self._client = client

    def clean_group(self, group_key, dry_run=True):
        """Cleans the group with a given key from duplicate labels."""
        gl_group = self._client.groups.get(group_key)
        group = Group(
            gl_api_object=gl_group,
            client=self._client,
            dry_run=dry_run,
        )

        self._mark_gl_group_redundant_labels(group, dry_run)

        if not dry_run:
            group.adjust_projects_nested_labels()

        self._clear_gl_group_from_marked_labels(group, dry_run)

        self._show_changes(group)

    def _show_changes(self, parent, indent=0) -> None:
        logger.debug(
            '{0} - {1}:'.format('\t' * indent, parent.gl_api_object.name),
        )
        indent += 1
        logger.debug('{0} Before: {1}'.format(
            '\t' * indent,
            [label.name for label in parent.initial_labels.values()],
        ))

        logger.debug('{0} After: {1}\n'.format(
            '\t' * indent,
            [
                label.name
                for label
                in parent.labels.values() if len(label.name.split('__')) != 3
            ],
        ))

        indent += 1
        if isinstance(parent, Group):
            for project in parent.projects:
                self._show_changes(project, indent)

            for subgroup in parent.subgroups:
                self._show_changes(subgroup, indent)

    def _mark_gl_group_redundant_labels(self, group, dry_run) -> None:
        self._rename_redundant_labels(group, dry_run)

        for project in group.projects:
            self._rename_redundant_labels(project, dry_run)

        for subgroup in group.subgroups:
            self._mark_gl_group_redundant_labels(subgroup, dry_run)

    def _clear_gl_group_from_marked_labels(self, group, dry_run) -> None:
        deleted: Set[int] = set()

        for gl_obj in (group, *group.projects):
            self._remove_marked_labels(
                labels=gl_obj.labels,
                gl_api_obj=gl_obj.gl_api_object,
                deleted=deleted,
                dry_run=dry_run,
            )

        for subgroup in group.subgroups:
            self._clear_gl_group_from_marked_labels(subgroup, dry_run)

    def _remove_marked_labels(
        self,
        labels,
        gl_api_obj,
        deleted,
        dry_run,
    ) -> None:
        """Deletes labels renamed with ___<id>__<count> pattern."""
        not_yet_deleted = [
            label
            for label
            in labels.values() if label.id not in deleted
        ]

        for label in not_yet_deleted:
            if len(label.name.split('__')) != 3:
                continue

            logger.debug(
                'Removing label {0} from {1}'.format(
                    label.name,
                    gl_api_obj.web_url,
                ),
            )

            deleted.add(label.id)

            if dry_run:
                return

            try:
                gl_api_obj.labels.delete(label.id)
            except GitlabDeleteError as exc:
                logger.debug(str(exc))

    def _rename_redundant_labels(self, group_or_project, dry_run=True) -> None:
        gl_api_obj = group_or_project.gl_api_object
        renamed_labels: Dict[int, Label] = {}

        for label in get_labels(gl_api_obj).values():
            if group_or_project.parent:
                if label.id in group_or_project.parent.labels:
                    continue

                match = get_label_match(
                    [
                        *renamed_labels.values(),
                        *group_or_project.parent.labels.values(),
                    ],
                    label,
                )
            else:
                match = get_label_match(list(renamed_labels.values()), label)

            if match:
                new_label = rename_label(
                    manager=gl_api_obj.labels,
                    old=label,
                    new=match,
                    dry_run=dry_run,
                )
                logger.debug('"{0}" will be renamed to "{1}"'.format(
                    label.name, new_label.name,
                ))
                renamed_labels[new_label.id] = new_label
            else:
                renamed_labels[label.id] = label

        group_or_project.labels = renamed_labels
        if group_or_project.parent:
            group_or_project.labels.update(group_or_project.parent.labels)


def rename_label(
    manager: Union[GroupLabelManager, ProjectLabelManager],
    old: Label,
    new: Label,
    dry_run: bool,
) -> Label:
    """Renames label to the form which helps us to set right parent labels."""
    counter = 1
    while counter:
        new_name = '__{0}__{1}'.format(new.id, counter)

        if dry_run:
            return Label(old.id, new_name)

        try:
            manager.update(old.id, {'new_name': new_name})

        except GitlabUpdateError:
            counter += 1

        else:
            return Label(old.id, new_name)
