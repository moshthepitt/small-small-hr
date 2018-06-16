"""
Module to test small_small_hr models
"""
from datetime import timedelta

from django.test import TestCase
from django.utils import timezone

from model_mommy import mommy


class TestScamModels(TestCase):
    """
    Test class for Scam models
    """

    def test_staffprofile_str(self):
        """
        Test that the __str__ method on StaffProfile works
        """
        user = mommy.make('auth.User', first_name='Mosh', last_name='Pitt')
        staff = user.staffprofile
        self.assertEqual('Mosh Pitt', staff.__str__())

    def test_get_leave_days_count(self):
        """
        Test get_leave_days_count
        """
        user = mommy.make('auth.User', first_name='Mosh', last_name='Pitt')
        staff = user.staffprofile
        mommy.make(
            'small_small_hr.Leave', staff=staff, start=timezone.now(),
            end=timezone.now() + timedelta(days=6))
        mommy.make(
            'small_small_hr.Leave', staff=staff, start=timezone.now(),
            end=timezone.now() + timedelta(days=5))
        self.assertEqual(timedelta(days=11).days,
                         staff.get_leave_days_count().days)

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
            f'Mosh Pitt: {now.time()} to {end.time()}',
            mommy.make(
                'small_small_hr.OverTime', start=now, end=end,
                staff=staff).__str__())
