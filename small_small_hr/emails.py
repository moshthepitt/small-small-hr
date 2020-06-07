"""Emails module for scam app."""
from django.conf import settings
from django.utils.translation import ugettext as _

from model_reviews.emails import send_email

from small_small_hr.models import Leave, OverTime


def leave_application_email(leave_obj: Leave):
    """Send an email to admins when a leave application is made."""
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
            template_path="small_small_hr/email",
        )


def leave_processed_email(leave_obj: Leave):
    """Send an email to admins when a leave application is processed."""
    if leave_obj.staff.user.email:
        msg = getattr(
            settings,
            "SSHR_LEAVE_PROCESSED_EMAIL_TXT",
            _(
                f"You leave application status is "
                f"{leave_obj.get_review_status_display()}.  Log in for more info."
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
            template_path="small_small_hr/email",
        )


def overtime_application_email(overtime_obj: OverTime):
    """Send an email to admins when an overtime application is made."""
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
            template_path="small_small_hr/email",
        )


def overtime_processed_email(overtime_obj: OverTime):
    """Send an email to admins when an overtime application is processed."""
    if overtime_obj.staff.user.email:

        msg = getattr(
            settings,
            "SSHR_OVERTIME_PROCESSED_EMAIL_TXT",
            _(
                f"You overtime application status is "
                f"{overtime_obj.get_review_status_display()}.  Log in for more info."
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
            template_path="small_small_hr/email",
        )
