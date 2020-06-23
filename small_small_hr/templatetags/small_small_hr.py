"""Template tags module."""
from django import template
from django.utils.translation import ugettext as _

from small_small_hr.constants import HOURS, MINUTES

register = template.Library()


@register.filter
def overtime_duration(time_delta):
    """Display overtime duration."""
    total_seconds = int(time_delta.total_seconds())
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60

    return f"{hours} {_(HOURS)} {minutes} {_(MINUTES)}"
