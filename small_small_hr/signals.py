"""
Small small HR signals module
"""
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

from small_small_hr.models import StaffProfile

USER = settings.AUTH_USER_MODEL


@receiver(post_save, sender=USER)
# pylint: disable=unused-argument
def create_staffprofile(sender, instance, created, **kwargs):
    """
    Create staffprofile when a user object is created
    """
    if created or not instance.staffprofile:
        # pylint: disable=unused-variable
        # pylint: disable=no-member
        profile, profile_created = \
            StaffProfile.objects.get_or_create(user=instance)
