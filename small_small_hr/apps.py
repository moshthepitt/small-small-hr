"""
Apps module for small-small-hr
"""
from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class SmallSmallHrConfig(AppConfig):
    """Apps config class."""
    name = 'small_small_hr'
    app_label = 'small_small_hr'
    verbose_name = _("Small Small HR")

    def ready(self):
        """Do stuff when the app is ready."""
        # pylint: disable=import-outside-toplevel,unused-import
        import small_small_hr.signals  # noqa

        # set up app settings
        from django.conf import settings
        import small_small_hr.settings as defaults
        for name in dir(defaults):
            if name.isupper() and not hasattr(settings, name):
                setattr(settings, name, getattr(defaults, name))
