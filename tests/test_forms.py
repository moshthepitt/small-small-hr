"""
Module to test small_small_hr models
"""

from django.test import RequestFactory, TestCase
from django.contrib.auth.models import AnonymousUser
from small_small_hr.forms import StaffProfileAdminForm
from small_small_hr.models import StaffProfile
from model_mommy import mommy


class TestForms(TestCase):
    """
    Test class for Scam models
    """

    def setUp(self):
        """
        Setup test class
        """
        self.factory = RequestFactory()

    def test_staff_profile_admin_form(self):
        """
        Test StaffProfileAdminForm
        """
        user = mommy.make('auth.User')

        request = self.factory.get('/')
        request.session = {}
        request.user = AnonymousUser()

        data = {
            'first_name': 'Bob',
            'last_name': 'Mbugua',
            'id_number': '123456789',
            'sex': StaffProfile.MALE,
            'nhif': '111111',
            'nssf': '222222',
            'pin_number': 'A0000000Y',
            'emergency_contact_name': 'Bob Father',
            'emergency_contact_number': '+254722111111',
            'phone': '+254722111111',
            'address': 'This is the address.',
            'birthday': '1996-01-27',
            'leave_days': 21,
            'sick_days': 9,
            'overtime_allowed': True,
            'start_date': '2017-09-25',
            'end_date': '2018-12-31',
        }

        form = StaffProfileAdminForm(data=data, instance=user.staffprofile,
                                     request=request)
        self.assertTrue(form.is_valid())
        form.save()

        user.refresh_from_db()
        staffprofile = user.staffprofile

        self.assertEqual('Bob Mbugua', user.staffprofile.get_name())
        self.assertEqual(StaffProfile.MALE, staffprofile.sex)
        self.assertEqual('+254722111111', staffprofile.phone.as_e164)
        self.assertEqual(21, staffprofile.leave_days)
        self.assertEqual(9, staffprofile.sick_days)
        self.assertEqual(True, staffprofile.overtime_allowed)
        self.assertEqual(9, staffprofile.sick_days)

        self.assertEqual('This is the address.', staffprofile.address)
        self.assertEqual('1996-01-27', str(staffprofile.birthday))
        self.assertEqual('2017-09-25', str(staffprofile.start_date))
        self.assertEqual('2018-12-31', str(staffprofile.end_date))

        self.assertEqual('123456789',
                         staffprofile.data['id_number'])
        self.assertEqual('111111',
                         staffprofile.data['nhif'])
        self.assertEqual('222222',
                         staffprofile.data['nssf'])
        self.assertEqual('A0000000Y',
                         staffprofile.data['pin_number'])
        self.assertEqual('Bob Father',
                         staffprofile.data['emergency_contact_name'])
        self.assertEqual('+254722111111',
                         staffprofile.data['emergency_contact_number'])