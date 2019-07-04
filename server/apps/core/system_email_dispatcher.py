from django.core.mail import mail_managers
from django.template.loader import get_template


class SystemEmailDispatcher:
    @staticmethod
    def mail_managers(subject, text):
        content = get_template('system_email_template.html')

        renderer = content.render(context={
            'title': subject,
            'text': text.replace('\n', '<br/>'),
        })

        mail_managers(subject, text, html_message=renderer)
