"""
Apps module for small-small-hr
"""
from django.apps import AppConfig


class SmallSmallHrConfig(AppConfig):
    """
    Apps config class
    """
    name = 'small_small_hr'
    app_label = 'small_small_hr'

    def ready(self):
        # pylint: disable=unused-variable
        import small_small_hr.signals  # noqa
