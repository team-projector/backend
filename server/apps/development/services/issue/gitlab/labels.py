# -*- coding: utf-8 -*-

from gitlab.v4.objects import Project as GlProject
from gitlab.v4.objects import ProjectIssue as GlProjectIssue

from apps.development.models import Issue, Label


def load_issue_labels(
    issue: Issue,
    gl_project: GlProject,
    gl_issue: GlProjectIssue,
) -> None:
    """Load labels for issue."""
    project_labels = getattr(gl_project, 'cached_labels', None)

    if project_labels is None:
        project_labels = gl_project.labels.list(all=True)
        gl_project.cached_labels = project_labels

    labels = []

    for label_title in gl_issue.labels:
        label = Label.objects.filter(
            title=label_title,
        ).first()

        if not label:
            gl_label = next(
                (
                    project_label
                    for project_label in project_labels
                    if project_label.name == label_title
                ),
                None,
            )

            if gl_label:
                label = Label.objects.create(
                    title=label_title,
                    color=gl_label.color,
                )

        if label:
            labels.append(label)

    issue.labels.set(labels)