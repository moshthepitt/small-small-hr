"""
Module to test small_small_hr serializers
"""
from django.test import TestCase

from model_mommy import mommy

from small_small_hr.serializers import StaffProfileSerializer


class TestSerializers(TestCase):
    """
    Test class for serializers
    """

    def test_staffprofileserializer_fields(self):
        """
        Test StaffProfileSerializer fields
        """
        user = mommy.make('auth.User', first_name='Bob', last_name='Ndoe')
        staffprofile = mommy.make('small_small_hr.StaffProfile', user=user)

        serializer_instance = StaffProfileSerializer(staffprofile)
        expected_fields = [
            'id',
            'created',
            'modified',
            'first_name',
            'last_name',
            'id_number',
            'phone',
            'sex',
            'role',
            'nhif',
            'nssf',
            'pin_number',
            'address',
            'birthday',
            'leave_days',
            'sick_days',
            'overtime_allowed',
            'start_date',
            'end_date',
            'emergency_contact_name',
            'emergency_contact_number',
        ]
        self.assertEqual(
            set(expected_fields),
            set(list(serializer_instance.data.keys()))
        )
