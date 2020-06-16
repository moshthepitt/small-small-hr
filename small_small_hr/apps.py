"""
Apps module for small-small-hr
"""
from django.apps import AppConfig
from django.db.models.signals import post_migrate
from django.utils.translation import gettext_lazy as _


def mptt_callback(sender, **kwargs):  # pylint: disable=unused-argument
    """
    Rebuild mptt tree.

    We need to do this so that for existing objects we can rebuild the mptt tree
    and set correct values for all the mptt fields.  This is necessary because we
    need to remove the defaults placed in the migrations file.
    """
    # pylint: disable=import-outside-toplevel
    from small_small_hr.models import StaffProfile

    StaffProfile.objects.rebuild()


class SmallSmallHrConfig(AppConfig):
    """Apps config class."""

    name = "small_small_hr"
    app_label = "small_small_hr"
    verbose_name = _("Small Small HR")

    def ready(self):
        """Do stuff when the app is ready."""
        # pylint: disable=import-outside-toplevel,unused-import

        # post migrate function
        post_migrate.connect(mptt_callback, sender=self)

        # signals
        import small_small_hr.signals  # noqa

        # set up app settings
        from django.conf import settings
        import small_small_hr.settings as defaults

        for name in dir(defaults):
            if name.isupper() and not hasattr(settings, name):
                setattr(settings, name, getattr(defaults, name))
