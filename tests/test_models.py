"""
Module to test small_small_hr models
"""
from datetime import datetime, timedelta

from django.conf import settings
from django.test import TestCase
from django.utils import timezone

import pytz
from model_mommy import mommy

from small_small_hr.models import Leave


class TestModels(TestCase):
    """
    Test class for Scam models
    """

    def test_annualleave_str(self):
        """
        Test the __str__ method on AnnualLeave
        """
        user = mommy.make('auth.User', first_name='Mosh', last_name='Pitt')
        staff = user.staffprofile
        self.assertEqual(
            '2018: Mosh Pitt Regular Leave',
            mommy.make(
                'small_small_hr.AnnualLeave', staff=staff, year=2018,
                leave_type=Leave.REGULAR).__str__()
        )

    def test_annualleave_get_leave_days_remaining(self):
        """
        Test get_leave_days_remaining
        """
        user = mommy.make('auth.User', first_name='Mosh', last_name='Pitt')
        staff = user.staffprofile
        annual_leave = mommy.make(
                'small_small_hr.AnnualLeave', staff=staff, year=2017,
                leave_type=Leave.REGULAR)

        # 12 days of leave
        start = datetime(
            2017, 6, 5, 0, 0, 0, tzinfo=pytz.timezone(settings.TIME_ZONE))
        end = datetime(
            2017, 6, 16, 0, 0, 0, tzinfo=pytz.timezone(settings.TIME_ZONE))

        # add some approved leave days
        mommy.make(
            'small_small_hr.Leave', staff=staff, start=start,
            end=end, leave_type=Leave.REGULAR,
            status=Leave.APPROVED)

        # get some rejected and pending leave days
        mommy.make(
            'small_small_hr.Leave', staff=staff, start=start,
            end=end, leave_type=Leave.REGULAR,
            status=Leave.REJECTED)
        mommy.make(
            'small_small_hr.Leave', staff=staff, start=start,
            end=end, leave_type=Leave.REGULAR,
            status=Leave.PENDING)

        annual_leave.refresh_from_db()

        # we should ave 21 - 12 leave days remaining
        self.assertEqual(
            21 - 12,
            annual_leave.get_leave_days_remaining()
        )

    def test_annualleave_cumulative_leave_taken(self):
        """
        Test get_cumulative_leave_taken
        """
        user = mommy.make('auth.User', first_name='Mosh', last_name='Pitt')
        staff = user.staffprofile
        annual_leave = mommy.make(
                'small_small_hr.AnnualLeave', staff=staff, year=2017,
                leave_type=Leave.REGULAR)

        start = datetime(
            2017, 6, 5, 0, 0, 0, tzinfo=pytz.timezone(settings.TIME_ZONE))
        end = datetime(
            2017, 6, 7, 0, 0, 0, tzinfo=pytz.timezone(settings.TIME_ZONE))

        # add some approved leave days
        mommy.make(
            'small_small_hr.Leave', staff=staff, start=start,
            end=end, leave_type=Leave.REGULAR,
            status=Leave.APPROVED)

        # get some rejected and pending leave days
        mommy.make(
            'small_small_hr.Leave', staff=staff, start=start,
            end=end, leave_type=Leave.REGULAR,
            status=Leave.REJECTED)
        mommy.make(
            'small_small_hr.Leave', staff=staff, start=start,
            end=end, leave_type=Leave.REGULAR,
            status=Leave.PENDING)

        annual_leave.refresh_from_db()
        self.assertEqual(
            3,
            annual_leave.get_cumulative_leave_taken().days
        )

        # add some approved leave days that fall between years
        start = datetime(
            2017, 12, 30, 0, 0, 0, tzinfo=pytz.timezone(settings.TIME_ZONE))
        end = datetime(
            2017, 12, 31, 0, 0, 0, tzinfo=pytz.timezone(settings.TIME_ZONE))
        mommy.make(
            'small_small_hr.Leave', staff=staff, start=start,
            end=end, leave_type=Leave.REGULAR,
            status=Leave.APPROVED)

        annual_leave.refresh_from_db()
        # we should have 5 days in 2017
        self.assertEqual(
            5,
            annual_leave.get_cumulative_leave_taken().days
        )

        start = datetime(
            2018, 1, 1, 0, 0, 0, tzinfo=pytz.timezone(settings.TIME_ZONE))
        end = start + timedelta(days=4)
        mommy.make(
            'small_small_hr.Leave', staff=staff, start=start,
            end=end, leave_type=Leave.REGULAR,
            status=Leave.APPROVED)

        # we should have 4 days in 2018
        annual_leave_2018 = mommy.make(
                'small_small_hr.AnnualLeave', staff=staff, year=2018,
                leave_type=Leave.REGULAR)
        self.assertEqual(
            5,
            annual_leave_2018.get_cumulative_leave_taken().days
        )

    def test_staffprofile_str(self):
        """
        Test that the __str__ method on StaffProfile works
        """
        user = mommy.make('auth.User', first_name='Mosh', last_name='Pitt')
        staff = user.staffprofile
        self.assertEqual('Mosh Pitt', staff.__str__())

    def test_get_approved_leave_days(self):
        """
        Test get_approved_leave_days
        """
        user = mommy.make('auth.User', first_name='Mosh', last_name='Pitt')
        staff = user.staffprofile
        mommy.make(
            'small_small_hr.Leave', staff=staff, start=timezone.now(),
            end=timezone.now() + timedelta(days=6), leave_type=Leave.REGULAR,
            status=Leave.APPROVED)
        mommy.make(
            'small_small_hr.Leave', staff=staff, start=timezone.now(),
            end=timezone.now() + timedelta(days=5), leave_type=Leave.REGULAR,
            status=Leave.APPROVED)
        self.assertEqual(timedelta(days=11).days,
                         staff.get_approved_leave_days().days)

    def test_get_approved_sick_days(self):
        """
        Test get_approved_sick_days
        """
        user = mommy.make('auth.User', first_name='Mosh', last_name='Pitt')
        staff = user.staffprofile
        mommy.make(
            'small_small_hr.Leave', staff=staff, start=timezone.now(),
            end=timezone.now() + timedelta(days=4), leave_type=Leave.SICK,
            status=Leave.APPROVED)
        mommy.make(
            'small_small_hr.Leave', staff=staff, start=timezone.now(),
            end=timezone.now() + timedelta(days=3), leave_type=Leave.SICK,
            status=Leave.APPROVED)
        self.assertEqual(timedelta(days=7).days,
                         staff.get_approved_sick_days().days)

    def test_role_str(self):
        """
        Test __str__ method on Role
        """
        self.assertEqual(
            'Accountant',
            mommy.make('small_small_hr.Role', name='Accountant').__str__()
        )

    def test_staffdocument_str(self):
        """
        Test __str__ method on StaffDocument
        """
        user = mommy.make('auth.User', first_name='Mosh', last_name='Pitt')
        staff = user.staffprofile
        self.assertEqual(
            'Mosh Pitt - Dossier',
            mommy.make(
                'small_small_hr.StaffDocument',
                name='Dossier', staff=staff).__str__())

    def test_leave_str(self):
        """
        Test __str__ method on Leave
        """
        user = mommy.make('auth.User', first_name='Mosh', last_name='Pitt')
        staff = user.staffprofile
        now = timezone.now()
        end = now + timedelta(days=3)
        self.assertEqual(
            f'Mosh Pitt: {now} to {end}',
            mommy.make(
                'small_small_hr.Leave', start=now, end=end,
                staff=staff).__str__())

    def test_overtime_str(self):
        """
        Test __str__ method on OverTime
        """
        user = mommy.make('auth.User', first_name='Mosh', last_name='Pitt')
        staff = user.staffprofile
        now = timezone.now()
        end = now + timedelta(seconds=60 * 60 * 3)
        self.assertEqual(
            f'Mosh Pitt: {now.date()} from {now.time()} to {end.time()}',
            mommy.make(
                'small_small_hr.OverTime', date=now.date(),
                start=now.time(), end=end.time(),
                staff=staff).__str__())

    def test_overtime_duration(self):
        """
        Test get_duration method on OverTime
        """
        user = mommy.make('auth.User', first_name='Mosh', last_name='Pitt')
        staff = user.staffprofile
        now = timezone.now()
        end = now + timedelta(seconds=60 * 60 * 3)
        self.assertEqual(
            timedelta(seconds=60 * 60 * 3).seconds,
            mommy.make(
                'small_small_hr.OverTime', date=now.date(),
                start=now.time(), end=end.time(),
                staff=staff).get_duration().seconds)
