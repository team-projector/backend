from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import get_template


class SystemEmailDispatcher:
    @staticmethod
    def mail_users(subject, text, recipient_list):
        content = get_template('system_email_template.html')

        renderer = content.render(context={
            'title': subject,
            'text': text.replace('\n', '<br/>'),
        })

        send_mail(
            subject=subject,
            message=text,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=recipient_list,
            html_message=renderer
        )