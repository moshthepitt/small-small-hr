"""
Emails module for scam app
"""
from django.conf import settings
from django.contrib.sites.models import Site
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.translation import ugettext as _


def send_email(
        name: str, email: str, subject: str, message: str, obj: object = None):
    """
    Sends a generic email
    """
    context = {
        'name': name,
        'subject': subject,
        'message': message,
        'object': obj,
        'SITE': Site.objects.get_current()
    }
    email_subject = render_to_string(
        'small_small_hr/email/generic_email_subject.txt',
        context).replace('\n', '')
    email_txt_body = render_to_string(
        'small_small_hr/email/generic_email_body.txt', context)
    email_html_body = render_to_string(
        'small_small_hr/email/generic_email_body.html', context
        ).replace('\n', '')

    subject = email_subject
    from_email = settings.DEFAULT_FROM_EMAIL
    to_email = f'{name} <{email}>'
    text_content = email_txt_body
    html_content = email_html_body
    msg = EmailMultiAlternatives(subject, text_content, from_email, [to_email])
    msg.attach_alternative(html_content, "text/html")

    return msg.send(fail_silently=True)


def leave_application_email(leave_obj: object):
    """
    Sends an email to admins when a leave application is made
    """
    msg = getattr(
        settings,
        'HR_LEAVE_APPLICATION_EMAIL_TXT',
        _("There has been a new leave application.  Please log in to process "
          "it."))
    subj = getattr(
        settings,
        'HR_LEAVE_APPLICATION_EMAIL_SUBJ',
        _("New Leave Application"))
    admin_emails = getattr(
        settings, 'HR_ADMIN_EMAILS', [settings.DEFAULT_FROM_EMAIL])

    for admin_email in admin_emails:
        send_email(
            name=leave_obj.staff.get_name(),
            email=admin_email,
            subject=subj,
            message=msg,
            obj=leave_obj
        )


def leave_processed_email(leave_obj: object):
    """
    Sends an email to admins when a leave application is processed
    """
    if leave_obj.staff.user.email:
        msg = getattr(
            settings, 'HR_LEAVE_PROCESSED_EMAIL_TXT',
            _(f"You leave application status is "
              f"{leave_obj.get_status_display()}.  Log in for more info.")
        )
        subj = getattr(
            settings, 'HR_LEAVE_PROCESSED_EMAIL_SUBJ',
            _("Your leave application has been processed"))

        send_email(
            name=leave_obj.staff.get_name(),
            email=leave_obj.staff.user.email,
            subject=subj,
            message=msg,
            obj=leave_obj
        )


def overtime_application_email(overtime_obj: object):
    """
    Sends an email to admins when an overtime application is made
    """
    msg = getattr(
        settings,
        'HR_OVERTIME_APPLICATION_EMAIL_TXT',
        _("There has been a new overtime application.  Please log in to "
          "process it."))
    subj = getattr(
        settings,
        'HR_OVERTIME_APPLICATION_EMAIL_SUBJ',
        _("New Overtime Application"))
    admin_emails = getattr(
        settings, 'HR_ADMIN_EMAILS', [settings.DEFAULT_FROM_EMAIL])

    for admin_email in admin_emails:
        send_email(
            name=overtime_obj.staff.get_name(),
            email=admin_email,
            subject=subj,
            message=msg,
            obj=overtime_obj
        )


def overtime_processed_email(overtime_obj: object):
    """
    Sends an email to admins when an overtime application is processed
    """
    if overtime_obj.staff.user.email:

        msg = getattr(
            settings, 'HR_OVERTIME_PROCESSED_EMAIL_TXT',
            _(f"You overtime application status is "
              f"{overtime_obj.get_status_display()}.  Log in for more info.")
        )
        subj = getattr(
            settings, 'HR_OVERTIME_PROCESSED_EMAIL_SUBJ',
            _("Your overtime application has been processed"))

        send_email(
            name=overtime_obj.staff.get_name(),
            email=overtime_obj.staff.user.email,
            subject=subj,
            message=msg,
            obj=overtime_obj
        )
