"""Emails module for scam app."""
from django.conf import settings
from django.utils.translation import ugettext as _

from model_reviews.emails import get_display_name, send_email
from model_reviews.models import ModelReview, Reviewer

from small_small_hr.constants import (
    LEAVE_APPLICATION_EMAIL_TEMPLATE,
    LEAVE_COMPLETED_EMAIL_TEMPLATE,
    OVERTIME_APPLICATION_EMAIL_TEMPLATE,
    OVERTIME_COMPLETED_EMAIL_TEMPLATE,
)
from small_small_hr.models import Leave, OverTime


def send_request_for_leave_review(reviewer: Reviewer):
    """Send email requesting a Leave review to one reviewer."""
    if reviewer.user.email:
        source = reviewer.review.content_object
        send_email(
            name=get_display_name(reviewer.user),
            email=reviewer.user.email,
            subject=source.review_request_email_subject,
            message=source.review_request_email_body,
            obj=reviewer.review,
            cc_list=None,
            template=LEAVE_APPLICATION_EMAIL_TEMPLATE,
            template_path=source.email_template_path,
        )


def send_request_for_overtime_review(reviewer: Reviewer):
    """Send email requesting a OverTime review to one reviewer."""
    if reviewer.user.email:
        source = reviewer.review.content_object
        send_email(
            name=get_display_name(reviewer.user),
            email=reviewer.user.email,
            subject=source.review_request_email_subject,
            message=source.review_request_email_body,
            obj=reviewer.review,
            cc_list=None,
            template=OVERTIME_APPLICATION_EMAIL_TEMPLATE,
            template_path=source.email_template_path,
        )


def send_leave_review_complete_notice(review_obj: ModelReview):
    """Send notice that Leave review is complete."""
    if not review_obj.needs_review() and review_obj.user:
        if review_obj.user.email:
            source = review_obj.content_object
            send_email(
                name=get_display_name(review_obj.user),
                email=review_obj.user.email,
                subject=source.review_complete_email_subject,
                message=source.review_complete_email_body,
                obj=review_obj,
                cc_list=None,
                template=LEAVE_COMPLETED_EMAIL_TEMPLATE,
                template_path=source.email_template_path,
            )


def send_overtime_review_complete_notice(review_obj: ModelReview):
    """Send notice that OverTime review is complete."""
    if not review_obj.needs_review() and review_obj.user:
        if review_obj.user.email:
            source = review_obj.content_object
            send_email(
                name=get_display_name(review_obj.user),
                email=review_obj.user.email,
                subject=source.review_complete_email_subject,
                message=source.review_complete_email_body,
                obj=review_obj,
                cc_list=None,
                template=OVERTIME_COMPLETED_EMAIL_TEMPLATE,
                template_path=source.email_template_path,
            )


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
