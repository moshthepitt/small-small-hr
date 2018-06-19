"""
Module to test small_small_hr models
"""
import os
from datetime import datetime, timedelta

from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import RequestFactory, TestCase, override_settings

import pytz
from model_mommy import mommy

from small_small_hr.forms import (AnnualLeaveForm, ApplyLeaveForm,
                                  ApplyOverTimeForm, LeaveForm, OverTimeForm,
                                  RoleForm, StaffDocumentForm,
                                  StaffProfileAdminCreateForm,
                                  StaffProfileAdminForm, StaffProfileUserForm)
from small_small_hr.models import Leave, OverTime, StaffProfile
from small_small_hr.serializers import StaffProfileSerializer

BASE_DIR = os.path.dirname(os.path.dirname(__file__))


class TestForms(TestCase):
    """
    Test class for Scam models
    """

    def setUp(self):
        """
        Setup test class
        """
        self.factory = RequestFactory()

    def test_annual_leave_form(self):
        """
        Test AnnualLeaveForm
        """
        user = mommy.make('auth.User', first_name='Bob', last_name='Ndoe')
        staffprofile = mommy.make('small_small_hr.StaffProfile', user=user)

        request = self.factory.get('/')
        request.session = {}
        request.user = AnonymousUser()

        data = {
            'staff': staffprofile.id,
            'year': 2018,
            'leave_type': Leave.REGULAR,
            'allowed_days': 21,
            'carried_over_days': 10
        }

        form = AnnualLeaveForm(data=data)
        self.assertTrue(form.is_valid())
        annual_leave = form.save()
        self.assertEqual(staffprofile, annual_leave.staff)
        self.assertEqual(2018, annual_leave.year)
        self.assertEqual(21, annual_leave.allowed_days)
        self.assertEqual(10, annual_leave.carried_over_days)
        self.assertEqual(Leave.REGULAR, annual_leave.leave_type)

        data2 = {
            'staff': staffprofile.id,
            'year': 2017,
            'leave_type': Leave.REGULAR,
            'allowed_days': 21,
            'carried_over_days': 5
        }

        form = AnnualLeaveForm(data=data2, instance=annual_leave)
        self.assertTrue(form.is_valid())
        form.save()
        annual_leave.refresh_from_db()
        self.assertEqual(staffprofile, annual_leave.staff)
        self.assertEqual(2017, annual_leave.year)
        self.assertEqual(21, annual_leave.allowed_days)
        self.assertEqual(5, annual_leave.carried_over_days)
        self.assertEqual(Leave.REGULAR, annual_leave.leave_type)

    def test_role_form(self):
        """
        Test RoleForm
        """
        request = self.factory.get('/')
        request.session = {}
        request.user = AnonymousUser()

        data = {
            'name': 'Accountant',
            'description': 'Keep accounts'
        }

        form = RoleForm(data=data)
        self.assertTrue(form.is_valid())
        role = form.save()
        self.assertEqual('Accountant', role.name)
        self.assertEqual('Keep accounts', role.description)

    def test_overtime_form_apply(self):
        """
        Test OverTimeForm
        """
        user = mommy.make('auth.User', first_name='Bob', last_name='Ndoe')
        staffprofile = mommy.make('small_small_hr.StaffProfile', user=user)

        request = self.factory.get('/')
        request.session = {}
        request.user = AnonymousUser()

        # 6 hours of overtime
        start = datetime(
            2017, 6, 5, 0, 0, 0, tzinfo=pytz.timezone(settings.TIME_ZONE))
        end = datetime(
            2017, 6, 5, 6, 0, 0, tzinfo=pytz.timezone(settings.TIME_ZONE))

        data = {
            'staff': staffprofile.id,
            'date': start.date(),
            'start': start.time(),
            'end': end.time(),
            'reason': 'Extra work',
        }

        form = ApplyOverTimeForm(data=data)
        self.assertTrue(form.is_valid())
        overtime = form.save()
        self.assertEqual(staffprofile, overtime.staff)
        self.assertEqual(start.date(), overtime.date)
        self.assertEqual(start.time(), overtime.start)
        self.assertEqual(end.time(), overtime.end)
        self.assertEqual(
            timedelta(seconds=3600 * 6).seconds,
            overtime.get_duration().seconds)
        self.assertEqual('Extra work', overtime.reason)
        self.assertEqual(OverTime.PENDING, overtime.status)
        self.assertEqual('', overtime.comments)

    def test_overtime_form_apply_no_overlap(self):
        """
        Test no overlaps on OverTime
        """
        user = mommy.make('auth.User', first_name='Bob', last_name='Ndoe')
        staffprofile = mommy.make('small_small_hr.StaffProfile', user=user)

        request = self.factory.get('/')
        request.session = {}
        request.user = AnonymousUser()

        # 6 hours of overtime
        start = datetime(
            2017, 6, 5, 0, 0, 0, tzinfo=pytz.timezone(settings.TIME_ZONE))
        end = datetime(
            2017, 6, 5, 6, 0, 0, tzinfo=pytz.timezone(settings.TIME_ZONE))

        mommy.make(
            'small_small_hr.OverTime', start=start.time(), end=end.time(),
            status=OverTime.APPROVED, date=start.date, staff=staffprofile)

        data = {
            'staff': staffprofile.id,
            'date': start.date(),
            'start': start.time(),
            'end': end.time(),
            'reason': 'Extra work',
        }

        form = ApplyOverTimeForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertEqual(3, len(form.errors.keys()))
        self.assertEqual(
            'you cannot have overlapping overtime hours on the same day',
            form.errors['start'][0]
        )
        self.assertEqual(
            'you cannot have overlapping overtime hours on the same day',
            form.errors['date'][0]
        )
        self.assertEqual(
            'you cannot have overlapping overtime hours on the same day',
            form.errors['end'][0]
        )

    def test_overtime_form_process(self):
        """
        Test OverTimeForm
        """
        user = mommy.make('auth.User', first_name='Bob', last_name='Ndoe')
        staffprofile = mommy.make('small_small_hr.StaffProfile', user=user)

        request = self.factory.get('/')
        request.session = {}
        request.user = AnonymousUser()

        # 6 hours of overtime
        start = datetime(
            2017, 6, 5, 0, 0, 0, tzinfo=pytz.timezone(settings.TIME_ZONE))
        end = datetime(
            2017, 6, 5, 6, 0, 0, tzinfo=pytz.timezone(settings.TIME_ZONE))

        data = {
            'staff': staffprofile.id,
            'date': start.date(),
            'start': start.time(),
            'end': end.time(),
            'reason': 'Extra work',
            'status': OverTime.APPROVED,
            'comments': 'Cool'
        }

        form = OverTimeForm(data=data)
        self.assertTrue(form.is_valid())
        overtime = form.save()
        self.assertEqual(staffprofile, overtime.staff)
        self.assertEqual(start.date(), overtime.date)
        self.assertEqual(start.time(), overtime.start)
        self.assertEqual(end.time(), overtime.end)
        self.assertEqual(
            timedelta(seconds=3600 * 6).seconds,
            overtime.get_duration().seconds)
        self.assertEqual('Extra work', overtime.reason)
        self.assertEqual(OverTime.APPROVED, overtime.status)
        self.assertEqual('Cool', overtime.comments)

    def test_overtime_form_start_end(self):
        """
        Test OverTimeForm start end fields
        """
        user = mommy.make('auth.User', first_name='Bob', last_name='Ndoe')
        staffprofile = mommy.make('small_small_hr.StaffProfile', user=user)

        request = self.factory.get('/')
        request.session = {}
        request.user = AnonymousUser()

        start = datetime(
            2017, 6, 5, 6, 0, 0, tzinfo=pytz.timezone(settings.TIME_ZONE))
        end = datetime(
            2017, 6, 5, 5, 0, 0, tzinfo=pytz.timezone(settings.TIME_ZONE))

        data = {
            'staff': staffprofile.id,
            'date': start.date(),
            'start': start.time(),
            'end': end.time(),
            'reason': 'Extra work',
        }

        form = OverTimeForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertEqual(1, len(form.errors.keys()))
        self.assertEqual(
            'end must be greater than start',
            form.errors['end'][0]
        )

    def test_leaveform_apply(self):
        """
        Test LeaveForm apply for leave
        """
        user = mommy.make('auth.User', first_name='Bob', last_name='Ndoe')
        staffprofile = mommy.make('small_small_hr.StaffProfile', user=user)
        staffprofile.leave_days = 21
        staffprofile.sick_days = 10
        staffprofile.save()

        request = self.factory.get('/')
        request.session = {}
        request.user = AnonymousUser()

        # 6 days of leave
        start = datetime(
            2017, 6, 5, 0, 0, 0, tzinfo=pytz.timezone(settings.TIME_ZONE))
        end = datetime(
            2017, 6, 10, 0, 0, 0, tzinfo=pytz.timezone(settings.TIME_ZONE))

        mommy.make('small_small_hr.AnnualLeave', staff=staffprofile, year=2017,
                   leave_type=Leave.REGULAR, carried_over_days=12)

        data = {
            'staff': staffprofile.id,
            'leave_type': Leave.REGULAR,
            'start': start,
            'end': end,
            'reason': 'Need a break',
        }

        form = ApplyLeaveForm(data=data)
        self.assertTrue(form.is_valid())
        leave = form.save()
        self.assertEqual(staffprofile, leave.staff)
        self.assertEqual(Leave.REGULAR, leave.leave_type)
        self.assertEqual(start, leave.start)
        self.assertEqual(end, leave.end)
        self.assertEqual(
            timedelta(days=5).days, (leave.end - leave.start).days)
        self.assertEqual('Need a break', leave.reason)
        self.assertEqual(Leave.PENDING, leave.status)
        self.assertEqual('', leave.comments)

    def test_leaveform_no_overlap(self):
        """
        Test LeaveForm no overlap
        """
        user = mommy.make('auth.User', first_name='Bob', last_name='Ndoe')
        staffprofile = mommy.make('small_small_hr.StaffProfile', user=user)
        staffprofile.leave_days = 21
        staffprofile.sick_days = 10
        staffprofile.save()

        request = self.factory.get('/')
        request.session = {}
        request.user = AnonymousUser()

        # 6 days of leave
        start = datetime(
            2017, 6, 5, 0, 0, 0, tzinfo=pytz.timezone(settings.TIME_ZONE))
        end = datetime(
            2017, 6, 10, 0, 0, 0, tzinfo=pytz.timezone(settings.TIME_ZONE))

        mommy.make('small_small_hr.AnnualLeave', staff=staffprofile, year=2017,
                   leave_type=Leave.REGULAR, carried_over_days=12)

        mommy.make('small_small_hr.Leave', leave_type=Leave.REGULAR,
                   start=start, end=end, status=Leave.APPROVED,
                   staff=staffprofile)

        data = {
            'staff': staffprofile.id,
            'leave_type': Leave.REGULAR,
            'start': start,
            'end': end,
            'reason': 'Need a break',
        }

        form = ApplyLeaveForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertEqual(2, len(form.errors.keys()))
        self.assertEqual(
            'you cannot have overlapping leave days',
            form.errors['start'][0]
        )
        self.assertEqual(
            'you cannot have overlapping leave days',
            form.errors['end'][0]
        )

    def test_leaveform_admin(self):
        """
        Test LeaveForm apply for leave
        """
        user = mommy.make('auth.User', first_name='Bob', last_name='Ndoe')
        staffprofile = mommy.make('small_small_hr.StaffProfile', user=user)
        staffprofile.leave_days = 21
        staffprofile.sick_days = 10
        staffprofile.save()

        request = self.factory.get('/')
        request.session = {}
        request.user = AnonymousUser()

        # 6 days of leave
        start = datetime(
            2017, 6, 5, 0, 0, 0, tzinfo=pytz.timezone(settings.TIME_ZONE))
        end = datetime(
            2017, 6, 10, 0, 0, 0, tzinfo=pytz.timezone(settings.TIME_ZONE))

        mommy.make('small_small_hr.AnnualLeave', staff=staffprofile, year=2017,
                   leave_type=Leave.REGULAR, carried_over_days=12)

        data = {
            'staff': staffprofile.id,
            'leave_type': Leave.REGULAR,
            'start': start,
            'end': end,
            'reason': 'Need a break',
            'status': Leave.APPROVED,
            'comments': 'Okay'
        }

        form = LeaveForm(data=data)
        self.assertTrue(form.is_valid())
        leave = form.save()
        self.assertEqual(staffprofile, leave.staff)
        self.assertEqual(Leave.REGULAR, leave.leave_type)
        self.assertEqual(start, leave.start)
        self.assertEqual(end, leave.end)
        self.assertEqual(
            timedelta(days=5).days, (leave.end - leave.start).days)
        self.assertEqual('Need a break', leave.reason)
        self.assertEqual(Leave.APPROVED, leave.status)
        self.assertEqual('Okay', leave.comments)

    def test_leaveform_process(self):
        """
        Test LeaveForm process
        """
        user = mommy.make('auth.User', first_name='Bob', last_name='Ndoe')
        staffprofile = mommy.make('small_small_hr.StaffProfile', user=user)
        staffprofile.leave_days = 21
        staffprofile.sick_days = 10
        staffprofile.save()

        request = self.factory.get('/')
        request.session = {}
        request.user = AnonymousUser()

        # 6 days of leave
        start = datetime(
            2017, 6, 5, 0, 0, 0, tzinfo=pytz.timezone(settings.TIME_ZONE))
        end = datetime(
            2017, 6, 10, 0, 0, 0, tzinfo=pytz.timezone(settings.TIME_ZONE))

        mommy.make('small_small_hr.AnnualLeave', staff=staffprofile, year=2017,
                   leave_type=Leave.REGULAR, carried_over_days=4)

        data = {
            'staff': staffprofile.id,
            'leave_type': Leave.REGULAR,
            'start': start,
            'end': end,
            'reason': 'Need a break',
            'comments': 'Just no',
            'status': Leave.REJECTED
        }

        form = LeaveForm(data=data)
        self.assertTrue(form.is_valid())
        leave = form.save()
        self.assertEqual(staffprofile, leave.staff)
        self.assertEqual(Leave.REGULAR, leave.leave_type)
        self.assertEqual(start, leave.start)
        self.assertEqual(end, leave.end)
        self.assertEqual(
            timedelta(days=5).days, (leave.end - leave.start).days)
        self.assertEqual('Need a break', leave.reason)
        self.assertEqual(Leave.REJECTED, leave.status)
        self.assertEqual('Just no', leave.comments)

    def test_sickleave_apply(self):
        """
        Test LeaveForm apply for sick leave
        """
        user = mommy.make('auth.User', first_name='Bob', last_name='Ndoe')
        staffprofile = mommy.make('small_small_hr.StaffProfile', user=user)
        staffprofile.leave_days = 21
        staffprofile.sick_days = 10
        staffprofile.save()

        request = self.factory.get('/')
        request.session = {}
        request.user = AnonymousUser()

        # 6 days of leave
        start = datetime(
            2017, 6, 5, 0, 0, 0, tzinfo=pytz.timezone(settings.TIME_ZONE))
        end = datetime(
            2017, 6, 10, 0, 0, 0, tzinfo=pytz.timezone(settings.TIME_ZONE))

        mommy.make('small_small_hr.AnnualLeave', staff=staffprofile, year=2017,
                   leave_type=Leave.SICK, carried_over_days=4)

        data = {
            'staff': staffprofile.id,
            'leave_type': Leave.SICK,
            'start': start,
            'end': end,
            'reason': 'Need a break',
        }

        form = ApplyLeaveForm(data=data)
        self.assertTrue(form.is_valid())
        leave = form.save()
        self.assertEqual(staffprofile, leave.staff)
        self.assertEqual(Leave.SICK, leave.leave_type)
        self.assertEqual(start, leave.start)
        self.assertEqual(end, leave.end)
        self.assertEqual(
            timedelta(days=5).days, (leave.end - leave.start).days)
        self.assertEqual('Need a break', leave.reason)
        self.assertEqual(Leave.PENDING, leave.status)
        self.assertEqual('', leave.comments)

    def test_sickleave_process(self):
        """
        Test LeaveForm process sick leave
        """
        user = mommy.make('auth.User', first_name='Bob', last_name='Ndoe')
        staffprofile = mommy.make('small_small_hr.StaffProfile', user=user)
        staffprofile.leave_days = 21
        staffprofile.sick_days = 10
        staffprofile.save()

        request = self.factory.get('/')
        request.session = {}
        request.user = AnonymousUser()

        # 6 days of leave
        start = datetime(
            2017, 6, 5, 0, 0, 0, tzinfo=pytz.timezone(settings.TIME_ZONE))
        end = datetime(
            2017, 6, 10, 0, 0, 0, tzinfo=pytz.timezone(settings.TIME_ZONE))

        mommy.make('small_small_hr.AnnualLeave', staff=staffprofile, year=2017,
                   leave_type=Leave.SICK, carried_over_days=4)

        data = {
            'staff': staffprofile.id,
            'leave_type': Leave.SICK,
            'start': start,
            'end': end,
            'reason': 'Need a break',
            'comments': 'Just no',
            'status': Leave.REJECTED
        }

        form = LeaveForm(data=data)
        self.assertTrue(form.is_valid())
        leave = form.save()
        self.assertEqual(staffprofile, leave.staff)
        self.assertEqual(Leave.SICK, leave.leave_type)
        self.assertEqual(start, leave.start)
        self.assertEqual(end, leave.end)
        self.assertEqual(
            timedelta(days=5).days, (leave.end - leave.start).days)
        self.assertEqual('Need a break', leave.reason)
        self.assertEqual(Leave.REJECTED, leave.status)
        self.assertEqual('Just no', leave.comments)

    def test_leaveform_start_end(self):
        """
        Test start and end
        """
        user = mommy.make('auth.User', first_name='Bob', last_name='Ndoe')
        staffprofile = mommy.make('small_small_hr.StaffProfile', user=user)
        staffprofile.leave_days = 21
        staffprofile.sick_days = 10
        staffprofile.save()

        request = self.factory.get('/')
        request.session = {}
        request.user = AnonymousUser()

        # 6 days of leave
        start = datetime(
            2017, 6, 5, 0, 0, 0, tzinfo=pytz.timezone(settings.TIME_ZONE))
        end = datetime(
            2017, 6, 1, 0, 0, 0, tzinfo=pytz.timezone(settings.TIME_ZONE))

        mommy.make('small_small_hr.AnnualLeave', staff=staffprofile, year=2017,
                   leave_type=Leave.SICK, carried_over_days=4)

        data = {
            'staff': staffprofile.id,
            'leave_type': Leave.SICK,
            'start': start,
            'end': end,
            'reason': 'Need a break'
        }

        form = LeaveForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertEqual(1, len(form.errors.keys()))
        self.assertEqual(
            'end must be greater than start',
            form.errors['end'][0]
        )

        # end year and start year must be the same

        end = datetime(
            2018, 6, 1, 0, 0, 0, tzinfo=pytz.timezone(settings.TIME_ZONE))

        data2 = {
            'staff': staffprofile.id,
            'leave_type': Leave.SICK,
            'start': start,
            'end': end,
            'reason': 'Need a break'
        }

        form2 = LeaveForm(data=data2)
        self.assertFalse(form2.is_valid())
        self.assertEqual(2, len(form2.errors.keys()))
        self.assertEqual(
            'start and end must be from the same year',
            form2.errors['start'][0]
        )
        self.assertEqual(
            'start and end must be from the same year',
            form2.errors['end'][0]
        )

    def test_leaveform_max_days(self):
        """
        Test leave days sufficient
        """
        user = mommy.make('auth.User', first_name='Bob', last_name='Ndoe')
        staffprofile = mommy.make('small_small_hr.StaffProfile', user=user)
        staffprofile.leave_days = 21
        staffprofile.sick_days = 10
        staffprofile.save()

        request = self.factory.get('/')
        request.session = {}
        request.user = AnonymousUser()

        # 6 days of leave
        start = datetime(
            2017, 6, 5, 0, 0, 0, tzinfo=pytz.timezone(settings.TIME_ZONE))
        end = datetime(
            2017, 7, 10, 0, 0, 0, tzinfo=pytz.timezone(settings.TIME_ZONE))

        mommy.make('small_small_hr.AnnualLeave', staff=staffprofile, year=2017,
                   leave_type=Leave.REGULAR, allowed_days=21)

        data = {
            'staff': staffprofile.id,
            'leave_type': Leave.REGULAR,
            'start': start,
            'end': end,
            'reason': 'Need a break'
        }

        form = LeaveForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertEqual(2, len(form.errors.keys()))
        self.assertEqual(
            'Not enough leave days. Available leave days are 21.00',
            form.errors['start'][0]
        )
        self.assertEqual(
            'Not enough leave days. Available leave days are 21.00',
            form.errors['end'][0]
        )

    def test_leaveform_max_sick_days(self):
        """
        Test sick days sufficient
        """
        user = mommy.make('auth.User', first_name='Bob', last_name='Ndoe')
        staffprofile = mommy.make('small_small_hr.StaffProfile', user=user)
        staffprofile.leave_days = 21
        staffprofile.sick_days = 10
        staffprofile.save()

        request = self.factory.get('/')
        request.session = {}
        request.user = AnonymousUser()

        # 6 days of leave
        start = datetime(
            2017, 6, 5, 0, 0, 0, tzinfo=pytz.timezone(settings.TIME_ZONE))
        end = datetime(
            2017, 6, 20, 0, 0, 0, tzinfo=pytz.timezone(settings.TIME_ZONE))

        mommy.make('small_small_hr.AnnualLeave', staff=staffprofile, year=2017,
                   leave_type=Leave.SICK, carried_over_days=0, allowed_days=10)

        data = {
            'staff': staffprofile.id,
            'leave_type': Leave.SICK,
            'start': start,
            'end': end,
            'reason': 'Need a break'
        }

        form = LeaveForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertEqual(2, len(form.errors.keys()))
        self.assertEqual(
            'Not enough sick days. Available sick days are 10.00',
            form.errors['start'][0]
        )
        self.assertEqual(
            'Not enough sick days. Available sick days are 10.00',
            form.errors['end'][0]
        )

    @override_settings(PRIVATE_STORAGE_ROOT='/tmp/')
    def test_staffdocumentform(self):
        """
        Test StaffDocumentForm
        """
        user = mommy.make('auth.User', first_name='Bob', last_name='Ndoe')
        staffprofile = mommy.make('small_small_hr.StaffProfile', user=user)

        request = self.factory.get('/')
        request.session = {}
        request.user = AnonymousUser()

        path = os.path.join(
            BASE_DIR, 'tests', 'fixtures', 'contract.pdf')

        with open(path, 'r+b') as contract_file:
            data = {
                'staff': staffprofile.id,
                'name': 'Employment Contract',
                'description': 'This is the employment contract!',
                'file': contract_file
            }

            file_dict = {
                'file': SimpleUploadedFile(
                    name=contract_file.name,
                    content=contract_file.read(),
                    content_type='application/pdf'
                )}

            form = StaffDocumentForm(data, file_dict)

            self.assertTrue(form.is_valid())
            doc = form.save()

            self.assertEqual(staffprofile, doc.staff)
            self.assertEqual('Employment Contract', doc.name)
            self.assertEqual(
                'This is the employment contract!', doc.description)

        with open(path, 'r+b') as contract_file:
            self.assertTrue(contract_file.read(), doc.file.read())

    def test_staff_profile_user_form(self):
        """
        Test StaffProfileUserForm
        """
        user = mommy.make('auth.User')
        staffprofile = mommy.make('small_small_hr.StaffProfile', user=user)

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
            'birthday': '1996-01-27'
        }

        form = StaffProfileUserForm(data=data, instance=staffprofile,
                                    request=request)
        self.assertTrue(form.is_valid())
        form.save()

        user.refresh_from_db()

        self.assertEqual('Bob Mbugua', user.staffprofile.get_name())
        self.assertEqual(StaffProfile.MALE, staffprofile.sex)
        self.assertEqual('+254722111111', staffprofile.phone.as_e164)

        self.assertEqual('This is the address.', staffprofile.address)
        self.assertEqual('1996-01-27', str(staffprofile.birthday))

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

    def test_staff_profile_admin_create_form(self):
        """
        Test StaffProfileAdminCreateForm
        """
        user = mommy.make('auth.User')

        request = self.factory.get('/')
        request.session = {}
        request.user = AnonymousUser()

        data = {
            'user': user.id,
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

        form = StaffProfileAdminCreateForm(data=data, request=request)
        self.assertTrue(form.is_valid())
        staffprofile = form.save()

        user.refresh_from_db()

        self.assertEqual('Bob Mbugua', user.staffprofile.get_name())
        self.assertEqual(StaffProfile.MALE, staffprofile.sex)
        self.assertEqual('+254722111111', staffprofile.phone.as_e164)
        self.assertEqual(21, staffprofile.leave_days)
        self.assertEqual(9, staffprofile.sick_days)
        self.assertEqual(True, staffprofile.overtime_allowed)

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

    def test_staff_profile_admin_form(self):
        """
        Test StaffProfileAdminForm
        """
        user = mommy.make('auth.User')
        staffprofile = mommy.make('small_small_hr.StaffProfile', user=user)

        request = self.factory.get('/')
        request.session = {}
        request.user = AnonymousUser()

        data = {
            'user': user.id,
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

        form = StaffProfileAdminForm(data=data, instance=staffprofile,
                                     request=request)
        self.assertTrue(form.is_valid())
        form.save()

        user.refresh_from_db()

        self.assertEqual('Bob Mbugua', user.staffprofile.get_name())
        self.assertEqual(StaffProfile.MALE, staffprofile.sex)
        self.assertEqual('+254722111111', staffprofile.phone.as_e164)
        self.assertEqual(21, staffprofile.leave_days)
        self.assertEqual(9, staffprofile.sick_days)
        self.assertEqual(True, staffprofile.overtime_allowed)

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

    def test_staffprofile_unique_pin_number(self):
        """
        Test unique pin_number
        """
        user = mommy.make('auth.User', first_name='Bob', last_name='Ndoe')
        staffprofile = mommy.make('small_small_hr.StaffProfile', user=user)
        staffprofile.data['id_number'] = '123456789'
        staffprofile.data['pin_number'] = '123456789'
        staffprofile.save()

        user2 = mommy.make('auth.User', first_name='Kyle', last_name='Ndoe')
        staffprofile2 = mommy.make('small_small_hr.StaffProfile', user=user2)
        staffprofile2.data['id_number'] = '9999999'
        staffprofile2.save()

        request = self.factory.get('/')
        request.session = {}
        request.user = AnonymousUser()

        data = StaffProfileSerializer(staffprofile2).data
        data['pin_number'] = '123456789'

        form = StaffProfileAdminForm(data=data,
                                     instance=staffprofile2,
                                     request=request)
        self.assertFalse(form.is_valid())
        self.assertEqual(1, len(form.errors.keys()))
        self.assertEqual(
            'This PIN number is already in use.',
            form.errors['pin_number'][0]
        )

    def test_staffprofile_unique_id_number(self):
        """
        Test unique id_number
        """
        user = mommy.make('auth.User', first_name='Bob', last_name='Ndoe')
        staffprofile = mommy.make('small_small_hr.StaffProfile', user=user)
        staffprofile.data['id_number'] = '123456789'
        staffprofile.save()

        user2 = mommy.make('auth.User', first_name='Kyle', last_name='Ndoe')
        staffprofile2 = mommy.make('small_small_hr.StaffProfile', user=user2)
        staffprofile2.save()

        request = self.factory.get('/')
        request.session = {}
        request.user = AnonymousUser()

        data = StaffProfileSerializer(staffprofile2).data
        data['id_number'] = '123456789'

        form = StaffProfileAdminForm(data=data,
                                     instance=staffprofile2,
                                     request=request)
        self.assertFalse(form.is_valid())
        self.assertEqual(1, len(form.errors.keys()))
        self.assertEqual(
            'This id number is already in use.',
            form.errors['id_number'][0]
        )

    def test_staffprofile_unique_nssf(self):
        """
        Test unique NSSF
        """
        user = mommy.make('auth.User', first_name='Bob', last_name='Ndoe')
        staffprofile = mommy.make('small_small_hr.StaffProfile', user=user)
        staffprofile.data['id_number'] = '123456789'
        staffprofile.data['nssf'] = '123456789'
        staffprofile.save()

        user2 = mommy.make('auth.User', first_name='Kyle', last_name='Ndoe')
        staffprofile2 = mommy.make('small_small_hr.StaffProfile', user=user2)
        staffprofile2.data['id_number'] = '9999999'
        staffprofile2.save()

        request = self.factory.get('/')
        request.session = {}
        request.user = AnonymousUser()

        data = StaffProfileSerializer(staffprofile2).data
        data['nssf'] = '123456789'

        form = StaffProfileAdminForm(data=data,
                                     instance=staffprofile2,
                                     request=request)
        self.assertFalse(form.is_valid())
        self.assertEqual(1, len(form.errors.keys()))
        self.assertEqual(
            'This NSSF number is already in use.',
            form.errors['nssf'][0]
        )

    def test_staffprofile_unique_nhif(self):
        """
        Test unique NHIF
        """
        user = mommy.make('auth.User', first_name='Bob', last_name='Ndoe')
        staffprofile = mommy.make('small_small_hr.StaffProfile', user=user)
        staffprofile.data['id_number'] = '123456789'
        staffprofile.data['nhif'] = '123456789'
        staffprofile.save()

        user2 = mommy.make('auth.User', first_name='Kyle', last_name='Ndoe')
        staffprofile2 = mommy.make('small_small_hr.StaffProfile', user=user2)
        staffprofile2.data['id_number'] = '9999999'
        staffprofile2.save()

        request = self.factory.get('/')
        request.session = {}
        request.user = AnonymousUser()

        data = StaffProfileSerializer(staffprofile2).data
        data['nhif'] = '123456789'

        form = StaffProfileAdminForm(data=data,
                                     instance=staffprofile2,
                                     request=request)
        self.assertFalse(form.is_valid())
        self.assertEqual(1, len(form.errors.keys()))
        self.assertEqual(
            'This NHIF number is already in use.',
            form.errors['nhif'][0]
        )
