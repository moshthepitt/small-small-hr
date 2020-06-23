"""Emails module for scam app."""
from model_reviews.emails import get_display_name, send_email
from model_reviews.models import ModelReview, Reviewer

from small_small_hr.constants import (
    LEAVE_APPLICATION_EMAIL_TEMPLATE,
    LEAVE_COMPLETED_EMAIL_TEMPLATE,
    OVERTIME_APPLICATION_EMAIL_TEMPLATE,
    OVERTIME_COMPLETED_EMAIL_TEMPLATE,
)


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
