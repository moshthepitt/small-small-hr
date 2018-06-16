"""
Small small HR model managers module
"""
from django.db import models


class LeaveManager(models.Manager):  # pylint: disable=too-few-public-methods
    """
    Custom manager for Leave model
    """

    def get_queryset(self):
        """
        Get the queryset
        """
        return super().get_queryset().annotate(
            duration=models.F('end')-models.F('start'))
