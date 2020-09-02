"""Review module for small-small-hr."""
from django.conf import settings
from django.contrib.auth.models import User  # pylint: disable = imported-auth-user
from django.db import models

from model_reviews.models import Reviewer

from small_small_hr.constants import STAFF


def set_staff_request_review_user(review_obj: models.Model):
    """
    Set user for Leave and Overtime requests.

    This is the default strategy of auto-setting the user for a review object.
    It simply sets the user using a field on the model object that is under review.
    """
    if not review_obj.user:
        object_under_review = review_obj.content_object
        staff_profile = getattr(object_under_review, STAFF, None)
        if staff_profile:
            review_obj.user = staff_profile.user


def set_staff_request_reviewer(review_obj: models.Model):
    """
    Set reviewer for Leave and Overtime requests.

    This is the strategy that will be used:

        1. Set it to the staff member's supervisor
        2. Additionally, set to all members of the Group named SSHR_ADMIN_USER_GROUP_NAME
    """
    if review_obj.user:
        staff_member = review_obj.user.staffprofile
        manager = staff_member.supervisor
        if (
            manager
            and not Reviewer.objects.filter(
                review=review_obj, user=manager.user
            ).exists()
        ):
            reviewer = Reviewer(review=review_obj, user=manager.user)
            reviewer.save()  # ensure save method is called

    hr_group_name = settings.SSHR_ADMIN_USER_GROUP_NAME
    for user in User.objects.filter(groups__name=hr_group_name):
        if not Reviewer.objects.filter(review=review_obj, user=user).exists():
            reviewer = Reviewer(review=review_obj, user=user)
            reviewer.save()  # ensure save method is called
