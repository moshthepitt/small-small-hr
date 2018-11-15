"""
Utils module for small small hr
"""
from datetime import timedelta
from decimal import Decimal
from django.db.models import Q
from django.conf import settings
from django.utils import timezone

from small_small_hr.models import AnnualLeave, Leave


def get_days(start: object, end: object):
    """
    Yield the days between two datetime objects
    """
    current_tz = timezone.get_current_timezone()
    local_start = current_tz.normalize(start)
    local_end = current_tz.normalize(end)
    span = local_end.date() - local_start.date()
    for i in range(span.days + 1):
        yield local_start.date() + timedelta(days=i)


def get_taken_leave_days(
        staffprofile: object,
        status: str,
        leave_type: str,
        start_year: int,
        end_year: int):
    """
    Calculate the number of leave days actually taken,
    taking into account weekends and weekend policy
    """
    count = Decimal(0)
    queryset = Leave.objects.filter(
        staff=staffprofile,
        status=status,
        leave_type=leave_type).filter(
            Q(start__year__gte=start_year) | Q(end__year__lte=end_year))
    for leave_obj in queryset:
        days = get_days(start=leave_obj.start, end=leave_obj.end)
        for day in days:
            if day.year >= start_year and day.year <= end_year:
                day_value = settings.SSHR_DAY_LEAVE_VALUES[day.isoweekday()]
                count = count + Decimal(day_value)
    return count


def get_carry_over(staffprofile: object, year: int, leave_type: str):
    """
    Get carried over leave days
    """
    # pylint: disable=no-member
    if leave_type == Leave.REGULAR:
        previous_obj = AnnualLeave.objects.filter(
            staff=staffprofile, year=year - 1, leave_type=leave_type).first()
        if previous_obj:
            remaining = previous_obj.get_available_leave_days()
            max_carry_over = settings.SSHR_MAX_CARRY_OVER
            if remaining > max_carry_over:
                carry_over = max_carry_over
            else:
                carry_over = remaining

            return carry_over

    return 0


def create_annual_leave(staffprofile: object, year: int, leave_type: str):
    """
    Creates an annuall leave object for the staff member
    """
    # pylint: disable=no-member
    try:
        annual_leave = AnnualLeave.objects.get(
            staff=staffprofile, year=year, leave_type=leave_type)
    except AnnualLeave.DoesNotExist:
        carry_over = get_carry_over(staffprofile, year, leave_type)

        if leave_type == Leave.REGULAR:
            allowed_days = staffprofile.leave_days
        elif leave_type == Leave.SICK:
            allowed_days = staffprofile.sick_days

        annual_leave = AnnualLeave(
            staff=staffprofile,
            year=year,
            leave_type=leave_type,
            allowed_days=allowed_days,
            carried_over_days=carry_over
        )
        annual_leave.save()

    return annual_leave
