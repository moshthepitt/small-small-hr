"""
Small small HR signals module
"""
from django.conf import settings

from small_small_hr.models import StaffProfile

USER = settings.AUTH_USER_MODEL


# pylint: disable=unused-argument
def create_staffprofile(sender, instance, created, **kwargs):
    """
    Create staffprofile when a user object is created

    This signal is not connected by default
    """
    if created or not instance.staffprofile:
        # pylint: disable=unused-variable
        # pylint: disable=no-member
        profile, profile_created = \
            StaffProfile.objects.get_or_create(user=instance)
