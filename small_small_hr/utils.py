"""
Utils module for small small hr
"""
from datetime import date

from django.conf import settings
from django.utils import timezone

from small_small_hr.models import AnnualLeave, FreeDay, Leave, StaffProfile


def get_carry_over(staffprofile: StaffProfile, year: int, leave_type: str):
    """Get carried over leave days."""
    # pylint: disable=no-member
    if leave_type == Leave.REGULAR:
        previous_obj = AnnualLeave.objects.filter(
            staff=staffprofile, year=year - 1, leave_type=leave_type
        ).first()
        if previous_obj:
            remaining = previous_obj.get_available_leave_days()
            max_carry_over = settings.SSHR_MAX_CARRY_OVER
            if remaining > max_carry_over:
                carry_over = max_carry_over
            else:
                carry_over = remaining

            return carry_over

    return 0


def create_annual_leave(staffprofile: StaffProfile, year: int, leave_type: str):
    """Creates an annual leave object for the staff member."""
    # pylint: disable=no-member
    try:
        annual_leave = AnnualLeave.objects.get(
            staff=staffprofile, year=year, leave_type=leave_type
        )
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
            carried_over_days=carry_over,
        )
        annual_leave.save()

    return annual_leave


def create_free_days(start_year: int = timezone.now().year, number_of_years: int = 11):
    """
    Create FreeDay records.

    :param start_year:  the year from which to start creating free days
    :param number_of_years: number of years to create free days objects
    """
    default_days = settings.SSHR_FREE_DAYS
    years = (start_year + _ for _ in range(number_of_years))
    for year in years:
        for default_day in default_days:
            the_date = date(
                year=year, month=default_day["month"], day=default_day["day"],
            )
            free_day = FreeDay(name=the_date.strftime("%A %d %B %Y"), date=the_date,)
            free_day.save()
