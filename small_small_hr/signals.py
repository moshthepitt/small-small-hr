from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

from small_small_hr.models import StaffProfile

User = settings.AUTH_USER_MODEL


@receiver(post_save, sender=User)
def create_staffprofile(sender, instance, created, **kwargs):
    if created or not instance.staffprofile:
        profile, profile_created = \
            StaffProfile.objects.get_or_create(user=instance)
