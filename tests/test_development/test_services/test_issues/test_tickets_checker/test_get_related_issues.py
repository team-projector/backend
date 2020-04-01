# -*- coding: utf-8 -*-

from apps.development.models.note import NoteType
from apps.development.services.issue.tickets_checker import get_related_issues
from tests.test_development.factories import IssueFactory, IssueNoteFactory


def test_no_related_issues(db):
    issue = IssueFactory.create(description="Empty string")

    assert not get_related_issues(issue).exists()


def test_issues_by_description(db):
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
    url_template = "https://gitlab.com/junte/team-projector/backend/issues/{0}"
    issue1 = IssueFactory.create(gl_url=url_template.format(12))
    issue2 = IssueFactory.create(gl_url=url_template.format(15))
    issue3 = IssueFactory.create()
    issue4 = IssueFactory.create(
        gl_url=url_template.format(14), description="",
    )

    note_params = {
        "content_object": issue4,
        "type": NoteType.COMMENT,
    }

    IssueNoteFactory.create(data={"numbers": ["12"]}, **note_params)
    IssueNoteFactory.create(data={"links": [issue2.gl_url]}, **note_params)

    related_issues = get_related_issues(issue4)

    assert related_issues.count() == 2
    assert related_issues.filter(id=issue1.id).exists()
    assert related_issues.filter(id=issue2.id).exists()
    assert not related_issues.filter(id=issue3.id).exists()
