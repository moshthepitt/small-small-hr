"""
Emails module for scam app
"""
from django.conf import settings
from django.contrib.sites.models import Site
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.translation import ugettext as _

from small_small_hr.models import Leave, OverTime


def send_email(  # pylint: disable=too-many-arguments,too-many-locals,bad-continuation
    name: str,
    email: str,
    subject: str,
    message: str,
    obj: object = None,
    cc_list: list = None,
    template: str = "generic",
    template_path: str = "small_small_hr/email",
):
    """
    Sends a generic email

    :param name: name of person
    :param email: email address to send to
    :param subject: the email's subject
    :param message: the email's body text
    :param obj: the object in question
    :param cc_list: the list of email address to "CC"
    :param template: the template to use
    """
    context = {
        "name": name,
        "subject": subject,
        "message": message,
        "object": obj,
        "SITE": Site.objects.get_current(),
    }
    email_subject = render_to_string(
        f"{template_path}/{template}_email_subject.txt", context
    ).replace("\n", "")
    email_txt_body = render_to_string(
        f"{template_path}/{template}_email_body.txt", context
    )
    email_html_body = render_to_string(
        f"{template_path}/{template}_email_body.html", context
    ).replace("\n", "")

    subject = email_subject
    from_email = settings.DEFAULT_FROM_EMAIL
    to_email = f"{name} <{email}>"
    text_content = email_txt_body
    html_content = email_html_body
    msg = EmailMultiAlternatives(subject, text_content, from_email, [to_email])
    if cc_list:
        msg.cc = cc_list
    msg.attach_alternative(html_content, "text/html")

    return msg.send(fail_silently=True)


def leave_application_email(leave_obj: Leave):
    """
    Sends an email to admins when a leave application is made
    """
    msg = getattr(
        settings,
        "SSHR_LEAVE_APPLICATION_EMAIL_TXT",
        _("There has been a new leave application.  Please log in to process " "it."),
    )
    subj = getattr(
        settings, "SSHR_LEAVE_APPLICATION_EMAIL_SUBJ", _("New Leave Application")
    )
    admin_emails = settings.SSHR_ADMIN_LEAVE_EMAILS

    for admin_email in admin_emails:
        send_email(
            name=settings.SSHR_ADMIN_NAME,
            email=admin_email,
            subject=subj,
            message=msg,
            obj=leave_obj,
            template="leave_application",
        )


def leave_processed_email(leave_obj: Leave):
    """
    Sends an email to admins when a leave application is processed
    """
    if leave_obj.staff.user.email:
        msg = getattr(
            settings,
            "SSHR_LEAVE_PROCESSED_EMAIL_TXT",
            _(
                f"You leave application status is "
                f"{leave_obj.get_status_display()}.  Log in for more info."
            ),
        )
        subj = getattr(
            settings,
            "SSHR_LEAVE_PROCESSED_EMAIL_SUBJ",
            _("Your leave application has been processed"),
        )

        send_email(
            name=leave_obj.staff.get_name(),
            email=leave_obj.staff.user.email,
            subject=subj,
            message=msg,
            obj=leave_obj,
            cc_list=settings.SSHR_ADMIN_LEAVE_EMAILS,
        )


def overtime_application_email(overtime_obj: OverTime):
    """
    Sends an email to admins when an overtime application is made
    """
    msg = getattr(
        settings,
        "SSHR_OVERTIME_APPLICATION_EMAIL_TXT",
        _(
            "There has been a new overtime application.  Please log in to "
            "process it."
        ),
    )
    subj = getattr(
        settings, "SSHR_OVERTIME_APPLICATION_EMAIL_SUBJ", _("New Overtime Application")
    )
    admin_emails = settings.SSHR_ADMIN_OVERTIME_EMAILS

    for admin_email in admin_emails:
        send_email(
            name=settings.SSHR_ADMIN_NAME,
            email=admin_email,
            subject=subj,
            message=msg,
            obj=overtime_obj,
            template="overtime_application",
        )


def overtime_processed_email(overtime_obj: OverTime):
    """
    Sends an email to admins when an overtime application is processed
    """
    if overtime_obj.staff.user.email:

        msg = getattr(
            settings,
            "SSHR_OVERTIME_PROCESSED_EMAIL_TXT",
            _(
                f"You overtime application status is "
                f"{overtime_obj.get_status_display()}.  Log in for more info."
            ),
        )
        subj = getattr(
            settings,
            "SSHR_OVERTIME_PROCESSED_EMAIL_SUBJ",
            _("Your overtime application has been processed"),
        )

        send_email(
            name=overtime_obj.staff.get_name(),
            email=overtime_obj.staff.user.email,
            subject=subj,
            message=msg,
            obj=overtime_obj,
            cc_list=settings.SSHR_ADMIN_OVERTIME_EMAILS,
        )
