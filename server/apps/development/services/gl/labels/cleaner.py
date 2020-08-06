# -*- coding: utf-8 -*-

import logging
from collections import namedtuple
from http import HTTPStatus
from typing import Dict, Generator, List, Optional, Union

from django.utils.functional import cached_property
from gitlab.v4.objects import Group as GLGroup
from gitlab.v4.objects import GroupProject as GLGroupProject

from apps.core.gitlab.client import get_default_gitlab_client
from apps.core.gitlab.utils.capture import capture_gitlab_requests

logger = logging.getLogger(__name__)


class Label:
    """Label object with label id, name and gl api parent refer."""

    def __init__(
        self, id_, name, parent: Union[GLGroupProject, GLGroup],
    ):
        """Inits a label."""
        self.id = id_  # noqa: WPS125, A003
        self.name = name
        self._parent = parent
        self.match_counter = 1

    def delete(self) -> None:
        """Deletes the label from gitlab."""
        logger.debug(
            "Removing label {0} from {1}".format(
                self.name, self._parent.web_url,
            ),
        )

        self._parent.labels.delete(self.id)

    def alt_name_to(self, target: "Label") -> None:
        """Renames a label to the name containing id of similar parent label."""
        new_name = "__{0}__{1}".format(target.id, target.match_counter)

        logger.debug(
            "'{0}' will be renamed to '{1}'".format(self.name, new_name),
        )

        self.name = new_name

    def find_match(self, label_list: List["Label"]) -> Optional["Label"]:
        """Having matching_label we look for the first match in label list."""
        for label in label_list:
            match_by_name = label.name.lower() == self.name.lower()

            if match_by_name and label.id != self.id:
                label.match_counter += 1
                return label

        return None


class LabelsContainer:
    """Such as group, project, merge request, issue."""

    def __init__(self, key, client) -> None:
        """Inits container with a client and gl_api_object."""
        self._key = key
        self._client = client
        self._labels: Optional[Dict[int, Label]] = None

    @cached_property
    def gl_api_object(self):
        """Returns interface to work with gitlab api."""
        raise NotImplementedError

    @property
    def labels(self):
        """Returns container labels without ancestors labels."""
        if self._labels is None:
            self._labels = self._get_labels()

        return self._labels

    def _get_labels(self) -> Dict[int, Label]:
        """Get labels for group or project and returns them as Label object."""
        labels = self.gl_api_object.labels.list(
            all=True, include_ancestor_groups=False,
        )

        return {
            gl_label.attributes.get("id"): Label(
                id_=gl_label.attributes.get("id"),
                name=gl_label.attributes.get("name"),
                parent=self.gl_api_object,
            )
            for gl_label in labels
        }


class Project(LabelsContainer):
    """Represents a gitlab project."""

    @cached_property
    def gl_api_object(self):
        """Returns project interface to work with gitlab api."""
        return self._client.projects.get(self._key)

    def adjust_work_items_labels(self) -> None:
        """
        Adjusting labels in every issue and merge_request of the project.

        After renaming redundant labels:
        "to do" => "__23232212__1"
        this adds to the issues or merge requests having "__23232212__1" label
        original parent label with id=23232212, so after running this the issue
        with labels ["__23232212__1"] will have ["__23232212__1", "To Do"]
        """
        for attr_name in "issues", "mergerequests":
            manager = getattr(self.gl_api_object, attr_name)
            for gl_api_obj in manager.list(all=True):
                self._adjust_labels_for_single_item(gl_api_obj)

    def _adjust_labels_for_single_item(self, gl_api_obj) -> None:
        initial = sorted(gl_api_obj.labels)
        gl_api_obj.labels = list(
            {
                self._replace_label_by_id(l_name)
                for l_name in gl_api_obj.labels
            },
        )

        if initial != sorted(gl_api_obj.labels):
            gl_api_obj.save()
            logger.debug(
                "Change labels for {0}:\n{1} -> {2}".format(
                    gl_api_obj.web_url, initial, gl_api_obj.labels,
                ),
            )

    def _replace_label_by_id(self, label_name) -> str:
        name_parts = label_name.split("__")
        if len(label_name.split("__")) != 3:
            return label_name

        if not name_parts[1].isnumeric():
            return label_name

        label_id = int(name_parts[1])
        label = self.labels.get(label_id)
        return label.name if label else label_name


class Group(LabelsContainer):
    """Represents a gitlab group."""

    @cached_property
    def gl_api_object(self):
        """Returns group interface to work with gitlab api."""
        return self._client.groups.get(self._key)

    def get_subgroups(self) -> List["Group"]:
        """Returns subgroups."""
        return [
            Group(key=subgroup.get_id(), client=self._client)
            for subgroup in self.gl_api_object.subgroups.list(all=True)
        ]

    def get_projects(self) -> List[Project]:
        """Returns projects."""
        return [
            Project(key=project.get_id(), client=self._client)
            for project in self.gl_api_object.projects.list(all=True)
        ]


TreeElement = namedtuple("TreeElement", ["container", "children"])


class LabelsContainerTree:
    """
    Tree of a group with all subgroups and projects.

    Class which build the tree using root element and provides easy access to
    all elements we need to work with.
    """

    def __init__(self, root_element: Union[Project, Group]):
        """Inits tree from the root element."""
        self.root = self.get_labels_containers_tree(root_element)

    @classmethod
    def get_labels_containers_tree(
        cls, root: Union[Project, Group], tree=None,
    ):
        """Builds tree from the element."""
        if not tree:
            tree = {}
        get_sub_tree = LabelsContainerTree.get_labels_containers_tree

        children = []
        if isinstance(root, Group):
            for subgroup in root.get_subgroups():
                children.append(get_sub_tree(subgroup))

            for project in root.get_projects():
                children.append(get_sub_tree(project))

        return TreeElement(root, children)

    def get_containers(
        self, element: Optional[TreeElement] = None,
    ) -> Generator[Union[Project, Group], None, None]:
        """Returns all containers in the tree."""
        if not element:
            element = self.root

        if isinstance(element.container, Project):
            yield element.container

        for child in element.children:
            yield from self.get_containers(child)

    def get_marked_labels(
        self, element: Optional[TreeElement] = None,
    ) -> Dict[int, Label]:
        """Returns all labels in the tree which have a form of __<id>__<n>."""
        if element is None:
            element = self.root

        ret = {
            label_id: label
            for label_id, label in element.container.labels.items()
            if len(label.name.split("__")) == 3
        }

        for child in element.children:
            ret.update(self.get_marked_labels(child))

        return ret


class LabelsCleaner:
    """Removes redundant labels, which have similar names from group."""

    def __init__(self, client=None):
        """Inits LabelsCleaner with gitlab client."""
        if not client:
            client = get_default_gitlab_client()
        self._client = client

    def clean_group(  # noqa:WPS210
        self, group_key: Union[str, int], dry_run=False,
    ):
        """Cleans the group with a given key from duplicate labels."""
        group = Group(group_key, client=self._client)

        operations = self._get_operations(group)

        if not dry_run:
            for num, operation in enumerate(operations, start=1):
                method, args, kwargs = operation
                try:
                    self._client.http_request(method, *args, **kwargs)

                except Exception:
                    logger.exception(
                        "Failed on {0} operation: {1}".format(num, operation),
                    )
                    break

        return operations

    def _get_operations(self, group: Group):
        tree = LabelsContainerTree(group)

        with capture_gitlab_requests(
            gl_client=self._client, put=HTTPStatus.OK, delete=HTTPStatus.OK,
        ) as captured:
            self._process_element_renaming(
                tree.root, tree.root.container.labels,
            )

            projects = [
                container
                for container in tree.get_containers()
                if isinstance(container, Project)
            ]

            for project in projects:
                project.adjust_work_items_labels()

            for label in tree.get_marked_labels().values():
                label.delete()

            return captured

    def _process_element_renaming(
        self, element: TreeElement, parent_labels: Dict[int, Label],
    ) -> None:
        parent_labels = parent_labels.copy()
        for label in element.container.labels.values():
            match = label.find_match(parent_labels.values())

            if not match:
                parent_labels[label.id] = label
                continue

            label.alt_name_to(match)
            parent_labels[label.id] = label

        for child in element.children:
            self._process_element_renaming(child, parent_labels)
