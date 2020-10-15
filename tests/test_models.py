"""Module to test small_small_hr models."""
from datetime import date, datetime, timedelta

from django.conf import settings
from django.test import TestCase, override_settings
from django.utils import timezone

import pytz
from model_mommy import mommy

from small_small_hr.models import FreeDay, Leave, get_taken_leave_days
from small_small_hr.utils import create_free_days

# pylint: disable=hard-coded-auth-user


class TestModels(TestCase):
    """Test class for models."""

    def test_annualleave_str(self):
        """Test the __str__ method on AnnualLeave."""
        user = mommy.make("auth.User", first_name="Mosh", last_name="Pitt")
        staff = mommy.make("small_small_hr.StaffProfile", user=user)
        self.assertEqual(
            "2018: Mosh Pitt Regular Leave",
            mommy.make(
                "small_small_hr.AnnualLeave",
                staff=staff,
                year=2018,
                leave_type=Leave.REGULAR,
            ).__str__(),
        )

    def test_freedays_str(self):
        """Test the __str__ method on FreeDay."""
        the_date = date(day=27, month=1, year=2017)
        self.assertEqual(
            "2017 - Friday 27 January 2017",
            mommy.make(
                "small_small_hr.FreeDay",
                name=the_date.strftime("%A %d %B %Y"),
                date=the_date,
            ).__str__(),
        )

    @override_settings(
        SSHR_DAY_LEAVE_VALUES={
            1: 1,  # Monday
            2: 1,  # Tuesday
            3: 1,  # Wednesday
            4: 1,  # Thursday
            5: 1,  # Friday
            6: 0.5,  # Saturday
            7: 0,  # Sunday
        }
    )
    def test_leave_day_count(self):
        """Test leave object day_count."""
        user = mommy.make("auth.User", first_name="Mosh", last_name="Pitt")
        staff = mommy.make("small_small_hr.StaffProfile", user=user)
        mommy.make(
            "small_small_hr.AnnualLeave",
            staff=staff,
            year=2017,
            leave_type=Leave.REGULAR,
            allowed_days=21,
        )
        mommy.make(
            "small_small_hr.FreeDay",
            name="RANDOM HOLIDAY",
            date=date(day=15, month=6, year=2017),
        )
        # 9.5 days of leave ==> Sun not counted, Sat = 0.5 and 15/6/2017 is holiday
        start = datetime(2017, 6, 5, 0, 0, 0, tzinfo=pytz.timezone(settings.TIME_ZONE))
        end = datetime(2017, 6, 16, 0, 0, 0, tzinfo=pytz.timezone(settings.TIME_ZONE))
        leave_obj = mommy.make(
            "small_small_hr.Leave",
            staff=staff,
            start=start,
            end=end,
            leave_type=Leave.REGULAR,
            review_status=Leave.APPROVED,
        )

        self.assertEqual(9.5, leave_obj.day_count)

    @override_settings(
        SSHR_DAY_LEAVE_VALUES={
            1: 1,  # Monday
            2: 1,  # Tuesday
            3: 1,  # Wednesday
            4: 1,  # Thursday
            5: 1,  # Friday
            6: 1,  # Saturday
            7: 1,  # Sunday
        }
    )
    def test_annualleave_get_available_leave_days(self):
        """Test get_available_leave_days."""
        user = mommy.make("auth.User", first_name="Mosh", last_name="Pitt")
        staff = mommy.make("small_small_hr.StaffProfile", user=user)
        annual_leave = mommy.make(
            "small_small_hr.AnnualLeave",
            staff=staff,
            year=2017,
            leave_type=Leave.REGULAR,
        )

        # 12 days of leave ==> Sat and Sun are counted
        start = datetime(2017, 6, 5, 0, 0, 0, tzinfo=pytz.timezone(settings.TIME_ZONE))
        end = datetime(2017, 6, 16, 0, 0, 0, tzinfo=pytz.timezone(settings.TIME_ZONE))

        # add some approved leave days
        mommy.make(
            "small_small_hr.Leave",
            staff=staff,
            start=start,
            end=end,
            leave_type=Leave.REGULAR,
            review_status=Leave.APPROVED,
        )

        # get some rejected and pending leave days
        mommy.make(
            "small_small_hr.Leave",
            staff=staff,
            start=start,
            end=end,
            leave_type=Leave.REGULAR,
            review_status=Leave.REJECTED,
        )
        mommy.make(
            "small_small_hr.Leave",
            staff=staff,
            start=start,
            end=end,
            leave_type=Leave.REGULAR,
            review_status=Leave.PENDING,
        )

        annual_leave.refresh_from_db()

        # we should ave 21 - 12 leave days remaining
        self.assertEqual(21 - 12, annual_leave.get_available_leave_days())

    @override_settings(
        SSHR_DAY_LEAVE_VALUES={
            1: 1,  # Monday
            2: 1,  # Tuesday
            3: 1,  # Wednesday
            4: 1,  # Thursday
            5: 1,  # Friday
            6: 0,  # Saturday
            7: 0,  # Sunday
        },
        SSHR_FREE_DAYS=[
            {"day": 8, "month": 6},  # MOSH DAY
            {"day": 6, "month": 1},  # PITT DAY
        ],  # these are days that are not counted when getting taken leave days
    )
    def test_annualleave_cumulative_leave_taken(self):
        """Test get_cumulative_leave_taken."""
        FreeDay.objects.all().delete()
        create_free_days(start_year=2017, number_of_years=24)

        user = mommy.make("auth.User", first_name="Mosh", last_name="Pitt")
        staff = mommy.make("small_small_hr.StaffProfile", user=user)
        annual_leave = mommy.make(
            "small_small_hr.AnnualLeave",
            staff=staff,
            year=2017,
            leave_type=Leave.REGULAR,
        )

        # note that 8/6/2017 is a FreeDay
        start = datetime(2017, 6, 5, 0, 0, 0, tzinfo=pytz.timezone(settings.TIME_ZONE))
        end = datetime(2017, 6, 8, 0, 0, 0, tzinfo=pytz.timezone(settings.TIME_ZONE))

        # add some 3 approved leave days
        mommy.make(
            "small_small_hr.Leave",
            staff=staff,
            start=start,
            end=end,
            leave_type=Leave.REGULAR,
            review_status=Leave.APPROVED,
        )

        # get some rejected and pending leave days
        mommy.make(
            "small_small_hr.Leave",
            staff=staff,
            start=start,
            end=end,
            leave_type=Leave.REGULAR,
            review_status=Leave.REJECTED,
        )
        mommy.make(
            "small_small_hr.Leave",
            staff=staff,
            start=start,
            end=end,
            leave_type=Leave.REGULAR,
            review_status=Leave.PENDING,
        )

        annual_leave.refresh_from_db()
        self.assertEqual(3, annual_leave.get_cumulative_leave_taken())

        # add some 2 approved leave days that fall between years
        # 1 day in 2017 and one in 2018
        # Dec 30 and Dec 31 are Sat, Sun which are not counted
        start = datetime(
            2017, 12, 29, 0, 0, 0, tzinfo=pytz.timezone(settings.TIME_ZONE)
        )
        end = datetime(2018, 1, 1, 0, 0, 0, tzinfo=pytz.timezone(settings.TIME_ZONE))
        mommy.make(
            "small_small_hr.Leave",
            staff=staff,
            start=start,
            end=end,
            leave_type=Leave.REGULAR,
            review_status=Leave.APPROVED,
        )

        annual_leave.refresh_from_db()
        # we should have 4 days in 2017
        self.assertEqual(4, annual_leave.get_cumulative_leave_taken())

        # add 4 days of leave // 6/1/2018 is not counted
        start = datetime(2018, 1, 2, 0, 0, 0, tzinfo=pytz.timezone(settings.TIME_ZONE))
        end = datetime(2018, 1, 6, 0, 0, 0, tzinfo=pytz.timezone(settings.TIME_ZONE))
        mommy.make(
            "small_small_hr.Leave",
            staff=staff,
            start=start,
            end=end,
            leave_type=Leave.REGULAR,
            review_status=Leave.APPROVED,
        )

        # we should have 5 days in 2018
        annual_leave_2018 = mommy.make(
            "small_small_hr.AnnualLeave",
            staff=staff,
            year=2018,
            leave_type=Leave.REGULAR,
        )
        self.assertEqual(5, annual_leave_2018.get_cumulative_leave_taken())

    def test_available_leave_days(self):
        """Test available leave days at various times of the year."""
        user = mommy.make("auth.User", first_name="Mosh", last_name="Pitt")
        staff = mommy.make("small_small_hr.StaffProfile", user=user)
        annual_leave = mommy.make(
            "small_small_hr.AnnualLeave",
            staff=staff,
            year=2017,
            leave_type=Leave.REGULAR,
            allowed_days=21,
            carried_over_days=0,
        )

        months = range(1, 13)

        for month in months:
            self.assertEqual(
                month * 1.75, annual_leave.get_available_leave_days(month=month)
            )

    def test_staffprofile_str(self):
        """Test that the __str__ method on StaffProfile works."""
        user = mommy.make("auth.User", first_name="Mosh", last_name="Pitt")
        staff = mommy.make("small_small_hr.StaffProfile", user=user)
        self.assertEqual("Mosh Pitt", staff.__str__())

    @override_settings(
        SSHR_DAY_LEAVE_VALUES={
            1: 1,  # Monday
            2: 1,  # Tuesday
            3: 1,  # Wednesday
            4: 1,  # Thursday
            5: 1,  # Friday
            6: 1,  # Saturday
            7: 1,  # Sunday
        }
    )
    def test_get_approved_leave_days(self):
        """Test get_approved_leave_days."""
        user = mommy.make("auth.User", first_name="Mosh", last_name="Pitt")
        staff = mommy.make("small_small_hr.StaffProfile", user=user)
        start = datetime(2018, 1, 1, 0, 0, 0, tzinfo=pytz.timezone(settings.TIME_ZONE))

        mommy.make(
            "small_small_hr.Leave",
            staff=staff,
            start=start,
            end=start + timedelta(days=6),
            leave_type=Leave.REGULAR,
            review_status=Leave.APPROVED,
        )
        mommy.make(
            "small_small_hr.Leave",
            staff=staff,
            start=start + timedelta(days=10),
            end=start + timedelta(days=14),
            leave_type=Leave.REGULAR,
            review_status=Leave.APPROVED,
        )
        self.assertEqual(
            timedelta(days=12).days, staff.get_approved_leave_days(year=start.year)
        )

    @override_settings(
        SSHR_DAY_LEAVE_VALUES={
            1: 1,  # Monday
            2: 1,  # Tuesday
            3: 1,  # Wednesday
            4: 1,  # Thursday
            5: 1,  # Friday
            6: 0,  # Saturday
            7: 0,  # Sunday
        }
    )
    def test_get_approved_sick_days(self):
        """Test get_approved_sick_days."""
        user = mommy.make("auth.User", first_name="Mosh", last_name="Pitt")
        staff = mommy.make("small_small_hr.StaffProfile", user=user)
        start = datetime(2018, 1, 1, 0, 0, 0, tzinfo=pytz.timezone(settings.TIME_ZONE))

        mommy.make(
            "small_small_hr.Leave",
            staff=staff,
            start=start,
            end=start + timedelta(days=4),
            leave_type=Leave.SICK,
            review_status=Leave.APPROVED,
        )
        mommy.make(
            "small_small_hr.Leave",
            staff=staff,
            start=start + timedelta(days=10),
            end=start + timedelta(days=15),
            leave_type=Leave.SICK,
            review_status=Leave.APPROVED,
        )
        self.assertEqual(
            timedelta(days=9).days, staff.get_approved_sick_days(year=start.year)
        )

    @override_settings(
        SSHR_DAY_LEAVE_VALUES={
            1: 1,  # Monday
            2: 1,  # Tuesday
            3: 1,  # Wednesday
            4: 1,  # Thursday
            5: 1,  # Friday
            6: 0,  # Saturday
            7: 0,  # Sunday
        }
    )
    def test_staffprofile_get_available_leave_days(self):
        """Test StaffProfile get_available_leave_days."""
        user = mommy.make("auth.User", first_name="Mosh", last_name="Pitt")
        staff = mommy.make("small_small_hr.StaffProfile", user=user)
        mommy.make(
            "small_small_hr.AnnualLeave",
            staff=staff,
            year=2017,
            leave_type=Leave.REGULAR,
            allowed_days=21,
        )

        # 10 days of leave because Saturday and Sunday are not counted
        start = datetime(2017, 6, 5, 0, 0, 0, tzinfo=pytz.timezone(settings.TIME_ZONE))
        end = datetime(2017, 6, 16, 0, 0, 0, tzinfo=pytz.timezone(settings.TIME_ZONE))

        # add some approved leave days
        mommy.make(
            "small_small_hr.Leave",
            staff=staff,
            start=start,
            end=end,
            leave_type=Leave.REGULAR,
            review_status=Leave.APPROVED,
        )

        staff.refresh_from_db()

        # remaining should be 21 - 10
        self.assertEqual(21 - 10, staff.get_available_leave_days(year=2017))

    @override_settings(
        SSHR_DAY_LEAVE_VALUES={
            1: 1,  # Monday
            2: 1,  # Tuesday
            3: 1,  # Wednesday
            4: 1,  # Thursday
            5: 1,  # Friday
            6: 0,  # Saturday
            7: 0,  # Sunday
        }
    )
    def test_one_leave_day(self):
        """Test one leave day."""
        user = mommy.make("auth.User", first_name="Mosh", last_name="Pitt")
        staff = mommy.make("small_small_hr.StaffProfile", user=user)
        mommy.make(
            "small_small_hr.AnnualLeave",
            staff=staff,
            year=2017,
            leave_type=Leave.REGULAR,
            allowed_days=21,
        )

        # ONE DAY of leave because Saturday and Sunday are not counted
        start = datetime(2017, 6, 5, 0, 0, 0, tzinfo=pytz.timezone(settings.TIME_ZONE))
        end = datetime(2017, 6, 5, 0, 0, 0, tzinfo=pytz.timezone(settings.TIME_ZONE))

        # add some approved leave days
        mommy.make(
            "small_small_hr.Leave",
            staff=staff,
            start=start,
            end=end,
            leave_type=Leave.REGULAR,
            review_status=Leave.APPROVED,
        )

        staff.refresh_from_db()

        # remaining should be 21 - 10
        self.assertEqual(1, staff.get_approved_leave_days(year=2017))
        self.assertEqual(20, staff.get_available_leave_days(year=2017))

    @override_settings(
        SSHR_DAY_LEAVE_VALUES={
            1: 1,  # Monday
            2: 1,  # Tuesday
            3: 1,  # Wednesday
            4: 1,  # Thursday
            5: 1,  # Friday
            6: 0.5,  # Saturday
            7: 0,  # Sunday
        }
    )
    def test_staffprofile_get_available_sick_days(self):
        """Test StaffProfile get_available_leave_days."""
        user = mommy.make("auth.User", first_name="Mosh", last_name="Pitt")
        staff = mommy.make("small_small_hr.StaffProfile", user=user)
        mommy.make(
            "small_small_hr.AnnualLeave",
            staff=staff,
            year=2017,
            leave_type=Leave.SICK,
            allowed_days=10,
        )

        # 6 days of leave
        start = datetime(2017, 6, 5, 0, 0, 0, tzinfo=pytz.timezone(settings.TIME_ZONE))
        end = datetime(2017, 6, 10, 0, 0, 0, tzinfo=pytz.timezone(settings.TIME_ZONE))

        # add some approved leave days
        mommy.make(
            "small_small_hr.Leave",
            staff=staff,
            start=start,
            end=end,
            leave_type=Leave.SICK,
            review_status=Leave.APPROVED,
        )

        staff.refresh_from_db()

        # remaining should be 10 - 6
        self.assertEqual(10 - 6, int(staff.get_available_sick_days(year=2017)))

    def test_role_str(self):
        """Test __str__ method on Role."""
        self.assertEqual(
            "Accountant", mommy.make("small_small_hr.Role", name="Accountant").__str__()
        )

    def test_staffdocument_str(self):
        """Test __str__ method on StaffDocument."""
        user = mommy.make("auth.User", first_name="Mosh", last_name="Pitt")
        staff = mommy.make("small_small_hr.StaffProfile", user=user)
        self.assertEqual(
            "Mosh Pitt - Dossier",
            mommy.make(
                "small_small_hr.StaffDocument", name="Dossier", staff=staff
            ).__str__(),
        )

    def test_leave_str(self):
        """Test __str__ method on Leave."""
        user = mommy.make("auth.User", first_name="Mosh", last_name="Pitt")
        staff = mommy.make("small_small_hr.StaffProfile", user=user)
        now = timezone.now()
        end = now + timedelta(days=3)
        self.assertEqual(
            f"Mosh Pitt: {now} to {end}",
            mommy.make(
                "small_small_hr.Leave", start=now, end=end, staff=staff
            ).__str__(),
        )

    def test_overtime_str(self):
        """Test __str__ method on OverTime."""
        user = mommy.make("auth.User", first_name="Mosh", last_name="Pitt")
        staff = mommy.make("small_small_hr.StaffProfile", user=user)
        now = timezone.now()
        end = now + timedelta(seconds=60 * 60 * 3)
        self.assertEqual(
            f"Mosh Pitt: {now.date()} from {now.time()} to {end.time()}",
            mommy.make(
                "small_small_hr.OverTime",
                date=now.date(),
                start=now.time(),
                end=end.time(),
                staff=staff,
            ).__str__(),
        )

    def test_overtime_duration(self):
        """Test get_duration method on OverTime."""
        user = mommy.make("auth.User", first_name="Mosh", last_name="Pitt")
        staff = mommy.make("small_small_hr.StaffProfile", user=user)
        now = timezone.now()
        end = now + timedelta(seconds=60 * 60 * 3)
        self.assertEqual(
            timedelta(seconds=60 * 60 * 3).seconds,
            mommy.make(
                "small_small_hr.OverTime",
                date=now.date(),
                start=now.time(),
                end=end.time(),
                staff=staff,
            )
            .get_duration()
            .seconds,
        )

    @override_settings(
        SSHR_DAY_LEAVE_VALUES={
            1: 1,  # Monday
            2: 1,  # Tuesday
            3: 1,  # Wednesday
            4: 1,  # Thursday
            5: 1,  # Friday
            6: 0,  # Saturday
            7: 0,  # Sunday
        }
    )
    def test_get_taken_leave_days(self):
        """Test get_taken_leave_days."""
        user = mommy.make("auth.User", first_name="Mosh", last_name="Pitt")
        staff = mommy.make("small_small_hr.StaffProfile", user=user)

        # 10 days of leave because Saturday and Sunday are not counted
        start = datetime(2017, 6, 5, 0, 0, 0, tzinfo=pytz.timezone(settings.TIME_ZONE))
        end = datetime(2017, 6, 16, 0, 0, 0, tzinfo=pytz.timezone(settings.TIME_ZONE))

        # add some approved leave days
        mommy.make(
            "small_small_hr.Leave",
            staff=staff,
            start=start,
            end=end,
            leave_type=Leave.REGULAR,
            review_status=Leave.APPROVED,
        )

        leave_days = get_taken_leave_days(
            staffprofile=staff,
            status=Leave.APPROVED,
            leave_type=Leave.REGULAR,
            start_year=2017,
            end_year=2017,
        )

        self.assertEqual(10, leave_days)

    @override_settings(
        SSHR_DAY_LEAVE_VALUES={
            1: 1,  # Monday
            2: 1,  # Tuesday
            3: 1,  # Wednesday
            4: 1,  # Thursday
            5: 1,  # Friday
            6: 0.5,  # Saturday
            7: 0,  # Sunday
        }
    )
    def test_get_taken_leave_days_half_saturday(self):
        """Test get_taken_leave_days."""
        user = mommy.make("auth.User", first_name="Kel", last_name="Vin")
        staff = mommy.make("small_small_hr.StaffProfile", user=user)

        # 10.5 days of leave because Saturday==0.5 and Sunday not counted
        start = datetime(2017, 6, 5, 0, 0, 0, tzinfo=pytz.timezone(settings.TIME_ZONE))
        end = datetime(2017, 6, 16, 0, 0, 0, tzinfo=pytz.timezone(settings.TIME_ZONE))

        # add some approved leave days
        mommy.make(
            "small_small_hr.Leave",
            staff=staff,
            start=start,
            end=end,
            leave_type=Leave.REGULAR,
            review_status=Leave.APPROVED,
        )

        leave_days = get_taken_leave_days(
            staffprofile=staff,
            status=Leave.APPROVED,
            leave_type=Leave.REGULAR,
            start_year=2017,
            end_year=2017,
        )

        self.assertEqual(10.5, leave_days)
