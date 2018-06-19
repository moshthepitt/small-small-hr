"""
Module to test small_small_hr Signals
"""
from django.db.models.signals import post_save
from django.test import TestCase

from model_mommy import mommy

from small_small_hr.models import StaffProfile
from small_small_hr.signals import create_staffprofile


class TestSignals(TestCase):
    """
    Test class for signals
    """

    def setUp(self):
        """
        Setup the Signal tests
        """
        post_save.connect(create_staffprofile, sender='auth.User',
                          dispatch_uid='create_staffprofile')

    def test_create_staffprofile(self):
        """
        Test create_staffprofile
        """
        user = mommy.make('auth.User', first_name='Bob', last_name='Ndoe')
        self.assertEqual(
            user.staffprofile,
            StaffProfile.objects.get(user=user)
        )
