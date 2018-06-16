"""
Small small HR model managers module
"""
from django.db import models


class LeaveManager(models.Manager):
    """
    Custom manager for Leave model
    """

    def get_queryset(self):
        """
        Get the queryset
        """
        return super().get_queryset().annotate(
            duration=models.F('end')-models.F('start'))