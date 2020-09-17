# -*- coding: utf-8 -*-

from apps.development.models.note import NoteType
from apps.development.services.issue.related import get_related_issues
from tests.test_development.factories import IssueFactory, IssueNoteFactory


def test_no_related_issues(db):
    """
    Test no related issues.

    :param db:
    """
    issue = IssueFactory.create(description="Empty string")

    assert not get_related_issues(issue).exists()


def test_issues_by_description(db):
    """
    Test issues by description.

    :param db:
    """
    url_template = "https://gitlab.com/junte/team-projector/backend/issues/{0}"
    issue1 = IssueFactory.create(gl_url=url_template.format(12))
    issue2 = IssueFactory.create(gl_url=url_template.format(15))
    issue3 = IssueFactory.create()

    issue4 = IssueFactory.create(
        gl_url=url_template.format(14),
        description="issue {0} #15".format(issue1.gl_url),
    )

    related_issues = get_related_issues(issue4)

    assert related_issues.count() == 2
    assert related_issues.filter(id=issue1.id).exists()
    assert related_issues.filter(id=issue2.id).exists()
    assert not related_issues.filter(id=issue3.id).exists()


def test_issues_by_note(db):
    """
    Test issues by note.

    :param db:
    """
    url_template = "https://gitlab.com/junte/team-projector/backend/issues/{0}"
    issue1 = IssueFactory.create(gl_url=url_template.format(12))
    issue2 = IssueFactory.create(gl_url=url_template.format(15))
    issue3 = IssueFactory.create()
    issue4 = IssueFactory.create(
        gl_url=url_template.format(14),
        description="",
    )

    note_params = {
        "content_object": issue4,
        "type": NoteType.COMMENT,
    }

    IssueNoteFactory.create(
        data={"issues": [issue1.gl_url, issue2.gl_url]},
        **note_params,
    )

    related_issues = get_related_issues(issue4)

    assert related_issues.count() == 2
    assert related_issues.filter(id=issue1.id).exists()
    assert related_issues.filter(id=issue2.id).exists()
    assert not related_issues.filter(id=issue3.id).exists()


def test_by_alternative(db):
    """
    Test by alternative.

    :param db:
    """
    url_template = "https://gitlab.com/junte/team-projector/backend/issues/{0}"
    alt_template = (
        "https://gitlab.com/junte/team-projector/backend/-/issues/{0}"
    )

    issues = [
        IssueFactory.create(gl_url=url_template.format(12), gl_iid=12),
        IssueFactory.create(gl_url=alt_template.format(15), gl_iid=15),
        IssueFactory.create(),
        IssueFactory.create(
            gl_url=url_template.format(14),
            description="",
            gl_iid=14,
        ),
    ]

    note_params = {
        "content_object": issues[3],
        "type": NoteType.COMMENT,
    }

    IssueNoteFactory.create(
        data={
            "issues": [
                alt_template.format(issues[0].gl_iid),
                url_template.format(issues[1].gl_iid),
            ],
        },
        **note_params,
    )

    related_issues = get_related_issues(issues[3])

    assert related_issues.count() == 2
    assert related_issues.filter(id=issues[0].id).exists()
    assert related_issues.filter(id=issues[1].id).exists()
    assert not related_issues.filter(id=issues[2].id).exists()
