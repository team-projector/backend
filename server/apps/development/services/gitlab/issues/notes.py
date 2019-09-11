from gitlab.v4.objects import ProjectIssue as GlProjectIssue

from apps.development.models import Issue, Note


def load_issue_notes(issue: Issue,
                     gl_issue: GlProjectIssue) -> None:
    for gl_note in gl_issue.notes.list(as_list=False, system=True):
        Note.objects.sync_gitlab(gl_note, issue)

    issue.adjust_spent_times()
