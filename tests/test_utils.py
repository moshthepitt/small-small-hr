"""Module to test small_small_hr Signals."""
from datetime import datetime

from django.conf import settings
from django.test import TestCase, override_settings

import pytz
from model_mommy import mommy

from small_small_hr.models import FreeDay, Leave, StaffProfile
from small_small_hr.utils import create_annual_leave, create_free_days, get_carry_over


class TestUtils(TestCase):
    """Test class for utils."""

    @override_settings(
        SSHR_MAX_CARRY_OVER=10,
        SSHR_DAY_LEAVE_VALUES={
            1: 1,  # Monday
            2: 1,  # Tuesday
            3: 1,  # Wednesday
            4: 1,  # Thursday
            5: 1,  # Friday
            6: 0,  # Saturday
            7: 0,  # Sunday
        },
    )
    def test_get_carry_over(self):
        """Test get_carry_over."""
        user = mommy.make("auth.User", id=23)
        StaffProfile.objects.all().delete()
        staffprofile = mommy.make("small_small_hr.StaffProfile", user=user)

        self.assertEqual(0, get_carry_over(staffprofile, 2017, Leave.REGULAR))

        create_annual_leave(staffprofile, 2017, Leave.REGULAR)

        # carry over should be 10 because the balance is 21
        self.assertEqual(10, get_carry_over(staffprofile, 2018, Leave.REGULAR))

        # 12 days of leave, Sat & Sun not counted
        start = datetime(2017, 6, 5, 0, 0, 0, tzinfo=pytz.timezone(settings.TIME_ZONE))
        end = datetime(2017, 6, 20, 0, 0, 0, tzinfo=pytz.timezone(settings.TIME_ZONE))

        mommy.make(
            "small_small_hr.Leave",
            leave_type=Leave.REGULAR,
            start=start,
            end=end,
            review_status=Leave.APPROVED,
            staff=staffprofile,
        )

        # carry over should be 9 => 21 - 12
        self.assertEqual(9, get_carry_over(staffprofile, 2018, Leave.REGULAR))

        # no sick leave carry over
        create_annual_leave(staffprofile, 2017, Leave.SICK)

        self.assertEqual(0, get_carry_over(staffprofile, 2018, Leave.SICK))

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
    def test_create_annual_leave(self):
        """Test create_annual_leave."""
        user = mommy.make("auth.User", id=56)
        StaffProfile.objects.all().delete()
        staffprofile = mommy.make("small_small_hr.StaffProfile", user=user)

        obj = create_annual_leave(staffprofile, 2016, Leave.REGULAR)

        self.assertEqual(staffprofile, obj.staff)
        self.assertEqual(2016, obj.year)
        self.assertEqual(0, obj.carried_over_days)
        self.assertEqual(21, obj.allowed_days)
        self.assertEqual(Leave.REGULAR, obj.leave_type)

        # 12 days of leave
        start = datetime(2016, 6, 5, 0, 0, 0, tzinfo=pytz.timezone(settings.TIME_ZONE))
        end = datetime(2016, 6, 16, 0, 0, 0, tzinfo=pytz.timezone(settings.TIME_ZONE))

        mommy.make(
            "small_small_hr.Leave",
            leave_type=Leave.REGULAR,
            start=start,
            end=end,
            review_status=Leave.APPROVED,
            staff=staffprofile,
        )

        obj2 = create_annual_leave(staffprofile, 2017, Leave.REGULAR)
        self.assertEqual(staffprofile, obj2.staff)
        self.assertEqual(2017, obj2.year)
        self.assertEqual(9, obj2.carried_over_days)
        self.assertEqual(21, obj2.allowed_days)
        self.assertEqual(Leave.REGULAR, obj2.leave_type)

        obj3 = create_annual_leave(staffprofile, 2018, Leave.SICK)
        self.assertEqual(staffprofile, obj3.staff)
        self.assertEqual(2018, obj3.year)
        self.assertEqual(0, obj3.carried_over_days)
        self.assertEqual(10, obj3.allowed_days)
        self.assertEqual(Leave.SICK, obj3.leave_type)

    @override_settings(
        SSHR_FREE_DAYS=[
            {"day": 1, "month": 1},  # New year
            {"day": 1, "month": 5},  # labour day
            {"day": 1, "month": 6},  # Madaraka day
            {"day": 20, "month": 10},  # Mashujaa day
            {"day": 12, "month": 12},  # Jamhuri day
            {"day": 25, "month": 12},  # Christmas
            {"day": 26, "month": 12},  # Boxing day
        ]
    )
    def test_create_free_days(self):
        """Test create_free_days."""
        FreeDay.objects.all().delete()
        create_free_days(start_year=2014, number_of_years=2)
        self.assertEqual(14, FreeDay.objects.count())
        self.assertTrue(
            FreeDay.objects.filter(date__year=2014, date__day=1, date__month=1).exists()
        )
        self.assertTrue(
            FreeDay.objects.filter(date__year=2014, date__day=1, date__month=5).exists()
        )
        self.assertTrue(
            FreeDay.objects.filter(date__year=2014, date__day=1, date__month=6).exists()
        )
        self.assertTrue(
            FreeDay.objects.filter(
                date__year=2014, date__day=20, date__month=10
            ).exists()
        )
        self.assertTrue(
            FreeDay.objects.filter(
                date__year=2014, date__day=12, date__month=12
            ).exists()
        )
        self.assertTrue(
            FreeDay.objects.filter(
                date__year=2014, date__day=25, date__month=12
            ).exists()
        )
        self.assertTrue(
            FreeDay.objects.filter(
                date__year=2014, date__day=26, date__month=12
            ).exists()
        )
        self.assertTrue(
            FreeDay.objects.filter(date__year=2015, date__day=1, date__month=1).exists()
        )
        self.assertTrue(
            FreeDay.objects.filter(date__year=2015, date__day=1, date__month=5).exists()
        )
        self.assertTrue(
            FreeDay.objects.filter(date__year=2015, date__day=1, date__month=6).exists()
        )
        self.assertTrue(
            FreeDay.objects.filter(
                date__year=2015, date__day=20, date__month=10
            ).exists()
        )
        self.assertTrue(
            FreeDay.objects.filter(
                date__year=2015, date__day=12, date__month=12
            ).exists()
        )
        self.assertTrue(
            FreeDay.objects.filter(
                date__year=2015, date__day=25, date__month=12
            ).exists()
        )
        self.assertTrue(
            FreeDay.objects.filter(
                date__year=2015, date__day=26, date__month=12
            ).exists()
        )
