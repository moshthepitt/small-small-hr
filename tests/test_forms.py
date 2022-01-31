"""Module to test small_small_hr models."""
# pylint: disable=too-many-lines,hard-coded-auth-user
import os
from datetime import date, datetime, timedelta

from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from django.contrib.contenttypes.models import ContentType
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import RequestFactory, TestCase, override_settings

import pytz
from model_mommy import mommy
from model_mommy.recipe import Recipe
from model_reviews.models import ModelReview

from small_small_hr.forms import (
    AnnualLeaveForm,
    ApplyLeaveForm,
    ApplyOverTimeForm,
    FreeDayForm,
    LeaveForm,
    OverTimeForm,
    RoleForm,
    StaffDocumentForm,
    StaffProfileAdminCreateForm,
    StaffProfileAdminForm,
    StaffProfileUserForm,
    UserStaffDocumentForm,
)
from small_small_hr.models import Leave, OverTime, StaffProfile, get_taken_leave_days
from small_small_hr.serializers import StaffProfileSerializer

BASE_DIR = os.path.dirname(os.path.dirname(__file__))


class TestForms(TestCase):  # pylint: disable=too-many-public-methods
    """Test class for forms."""

    def setUp(self):
        """Set up test class."""
        self.factory = RequestFactory()
        StaffProfile.objects.rebuild()
        self.manager = mommy.make(
            "auth.User", first_name="Jane", last_name="Ndoe", email="jane@example.com"
        )
        self.user = mommy.make(
            "auth.User", first_name="Bob", last_name="Ndoe", email="bob@example.com"
        )
        manager_mommy = Recipe(StaffProfile, lft=None, rght=None, user=self.manager)
        staff_mommy = Recipe(StaffProfile, lft=None, rght=None, user=self.user)
        self.manager_profile = manager_mommy.make()
        self.staffprofile = staff_mommy.make()

    def test_annual_leave_form(self):
        """Test AnnualLeaveForm."""
        user = mommy.make("auth.User", first_name="Bob", last_name="Ndoe")
        staffprofile = mommy.make("small_small_hr.StaffProfile", user=user)

        request = self.factory.get("/")
        request.session = {}
        request.user = AnonymousUser()

        data = {
            "staff": staffprofile.id,
            "year": 2018,
            "leave_type": Leave.REGULAR,
            "allowed_days": 21,
            "carried_over_days": 10,
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
            "staff": staffprofile.id,
            "year": 2017,
            "leave_type": Leave.REGULAR,
            "allowed_days": 21,
            "carried_over_days": 5,
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

    def test_annual_leave_form_decimals(self):
        """Test AnnualLeaveForm with decimal days."""
        user = mommy.make("auth.User", first_name="Bob", last_name="Ndoe")
        staffprofile = mommy.make("small_small_hr.StaffProfile", user=user)

        request = self.factory.get("/")
        request.session = {}
        request.user = AnonymousUser()

        data = {
            "staff": staffprofile.id,
            "year": 2018,
            "leave_type": Leave.REGULAR,
            "allowed_days": 16.5,
            "carried_over_days": 8.5,
        }

        form = AnnualLeaveForm(data=data)
        self.assertTrue(form.is_valid())
        annual_leave = form.save()
        self.assertEqual(staffprofile, annual_leave.staff)
        self.assertEqual(2018, annual_leave.year)
        self.assertEqual(16.5, annual_leave.allowed_days)
        self.assertEqual(8.5, annual_leave.carried_over_days)
        self.assertEqual(Leave.REGULAR, annual_leave.leave_type)

        data2 = {
            "staff": staffprofile.id,
            "year": 2017,
            "leave_type": Leave.REGULAR,
            "allowed_days": 21,
            "carried_over_days": 5,
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
        """Test RoleForm."""
        request = self.factory.get("/")
        request.session = {}
        request.user = AnonymousUser()

        data = {"name": "Accountant", "description": "Keep accounts"}

        form = RoleForm(data=data)
        self.assertTrue(form.is_valid())
        role = form.save()
        self.assertEqual("Accountant", role.name)
        self.assertEqual("Keep accounts", role.description)

    def test_freeday_form(self):
        """Test FreeDayForm."""
        request = self.factory.get("/")
        request.session = {}
        request.user = AnonymousUser()

        data = {"name": "Mosh Day", "date": "1/1/2017"}

        form = FreeDayForm(data=data)
        self.assertTrue(form.is_valid())
        free_day = form.save()
        self.assertEqual("Mosh Day", free_day.name)
        self.assertEqual(date(2017, 1, 1), free_day.date)

        # has to be unique
        form2 = FreeDayForm(data=data)
        self.assertFalse(form2.is_valid())
        self.assertEqual(1, len(form2.errors.keys()))
        self.assertEqual(
            "Free Day with this Date already exists.", form2.errors["date"][0]
        )

    def test_overtime_form_apply(self):
        """Test OverTimeForm."""
        user = mommy.make("auth.User", first_name="Bob", last_name="Ndoe")
        staffprofile = mommy.make("small_small_hr.StaffProfile", user=user)

        request = self.factory.get("/")
        request.session = {}
        request.user = AnonymousUser()

        # 6 hours of overtime
        start = datetime(2017, 6, 5, 0, 0, 0, tzinfo=pytz.timezone(settings.TIME_ZONE))
        end = datetime(2017, 6, 5, 6, 0, 0, tzinfo=pytz.timezone(settings.TIME_ZONE))

        data = {
            "staff": staffprofile.id,
            "date": start.date(),
            "start": start.time(),
            "end": end.time(),
            "review_reason": "Extra work",
        }

        form = ApplyOverTimeForm(data=data)
        self.assertTrue(form.is_valid())
        overtime = form.save()
        self.assertEqual(staffprofile, overtime.staff)
        self.assertEqual(start.date(), overtime.date)
        self.assertEqual(start.time(), overtime.start)
        self.assertEqual(end.time(), overtime.end)
        self.assertEqual(
            timedelta(seconds=3600 * 6).seconds, overtime.get_duration().seconds
        )
        self.assertEqual("Extra work", overtime.review_reason)
        self.assertEqual(OverTime.PENDING, overtime.review_status)

    def test_overtime_form_apply_no_overlap(self):
        """Test no overlaps on OverTime."""
        user = mommy.make("auth.User", first_name="Bob", last_name="Ndoe")
        staffprofile = mommy.make("small_small_hr.StaffProfile", user=user)

        request = self.factory.get("/")
        request.session = {}
        request.user = AnonymousUser()

        # 6 hours of overtime
        start = datetime(2017, 6, 5, 0, 0, 0, tzinfo=pytz.timezone(settings.TIME_ZONE))
        end = datetime(2017, 6, 5, 6, 0, 0, tzinfo=pytz.timezone(settings.TIME_ZONE))

        mommy.make(
            "small_small_hr.OverTime",
            start=start.time(),
            end=end.time(),
            review_status=OverTime.APPROVED,
            date=start.date,
            staff=staffprofile,
        )

        data = {
            "staff": staffprofile.id,
            "date": start.date(),
            "start": start.time(),
            "end": end.time(),
            "review_reason": "Extra work",
        }

        form = ApplyOverTimeForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertEqual(3, len(form.errors.keys()))
        self.assertEqual(
            "you cannot have overlapping overtime hours on the same day",
            form.errors["start"][0],
        )
        self.assertEqual(
            "you cannot have overlapping overtime hours on the same day",
            form.errors["date"][0],
        )
        self.assertEqual(
            "you cannot have overlapping overtime hours on the same day",
            form.errors["end"][0],
        )

    def test_overtime_form_process(self):
        """Test OverTimeForm."""
        user = mommy.make("auth.User", first_name="Bob", last_name="Ndoe")
        staffprofile = mommy.make("small_small_hr.StaffProfile", user=user)

        request = self.factory.get("/")
        request.session = {}
        request.user = AnonymousUser()

        # 6 hours of overtime
        start = datetime(2017, 6, 5, 0, 0, 0, tzinfo=pytz.timezone(settings.TIME_ZONE))
        end = datetime(2017, 6, 5, 6, 0, 0, tzinfo=pytz.timezone(settings.TIME_ZONE))

        data = {
            "staff": staffprofile.id,
            "date": start.date(),
            "start": start.time(),
            "end": end.time(),
            "review_reason": "Extra work",
            "review_status": OverTime.APPROVED,
        }

        form = OverTimeForm(data=data)
        self.assertTrue(form.is_valid())
        overtime = form.save()
        self.assertEqual(staffprofile, overtime.staff)
        self.assertEqual(start.date(), overtime.date)
        self.assertEqual(start.time(), overtime.start)
        self.assertEqual(end.time(), overtime.end)
        self.assertEqual(
            timedelta(seconds=3600 * 6).seconds, overtime.get_duration().seconds
        )
        self.assertEqual("Extra work", overtime.review_reason)
        self.assertEqual(OverTime.APPROVED, overtime.review_status)

    def test_overtime_form_process_with_overlap(self):
        """Test OverTimeForm with overlap for existing objects."""
        user = mommy.make("auth.User", first_name="Bob", last_name="Ndoe")
        staffprofile = mommy.make("small_small_hr.StaffProfile", user=user)

        request = self.factory.get("/")
        request.session = {}
        request.user = AnonymousUser()

        # 6 hours of overtime
        start = datetime(2017, 6, 5, 18, 0, 0, tzinfo=pytz.timezone(settings.TIME_ZONE))
        end = datetime(2017, 6, 5, 19, 0, 0, tzinfo=pytz.timezone(settings.TIME_ZONE))

        # make sure object already exists
        mommy.make(
            "small_small_hr.OverTime",
            start=start.time(),
            end=end.time(),
            review_status=OverTime.APPROVED,
            date=start.date,
            staff=staffprofile,
        )

        data = {
            "staff": staffprofile.id,
            "date": start.date(),
            "start": start.time(),
            "end": end.time(),
            "review_reason": "Extra work",
            "review_status": OverTime.REJECTED,
        }

        form = OverTimeForm(data=data)
        self.assertTrue(form.is_valid())
        overtime = form.save()
        self.assertEqual(staffprofile, overtime.staff)
        self.assertEqual(start.date(), overtime.date)
        self.assertEqual(start.time(), overtime.start)
        self.assertEqual(end.time(), overtime.end)
        self.assertEqual(
            timedelta(seconds=3600).seconds, overtime.get_duration().seconds
        )
        self.assertEqual("Extra work", overtime.review_reason)
        self.assertEqual(OverTime.REJECTED, overtime.review_status)

    def test_overtime_form_start_end(self):
        """Test OverTimeForm start end fields."""
        user = mommy.make("auth.User", first_name="Bob", last_name="Ndoe")
        staffprofile = mommy.make("small_small_hr.StaffProfile", user=user)

        request = self.factory.get("/")
        request.session = {}
        request.user = AnonymousUser()

        start = datetime(2017, 6, 5, 6, 0, 0, tzinfo=pytz.timezone(settings.TIME_ZONE))
        end = datetime(2017, 6, 5, 5, 0, 0, tzinfo=pytz.timezone(settings.TIME_ZONE))

        data = {
            "staff": staffprofile.id,
            "date": start.date(),
            "start": start.time(),
            "end": end.time(),
            "review_reason": "Extra work",
        }

        form = OverTimeForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertEqual(1, len(form.errors.keys()))
        self.assertEqual("end must be greater than start", form.errors["end"][0])

    @override_settings(SSHR_DEFAULT_TIME=7)
    def test_leaveform_apply(self):
        """Test LeaveForm apply for leave."""
        user = mommy.make("auth.User", first_name="Bob", last_name="Ndoe")
        staffprofile = mommy.make("small_small_hr.StaffProfile", user=user)
        staffprofile.leave_days = 21
        staffprofile.sick_days = 10
        staffprofile.save()

        request = self.factory.get("/")
        request.session = {}
        request.user = AnonymousUser()

        # 6 days of leave
        start = datetime(2017, 6, 5, 7, 0, 0, tzinfo=pytz.timezone(settings.TIME_ZONE))
        end = datetime(2017, 6, 10, 7, 0, 0, tzinfo=pytz.timezone(settings.TIME_ZONE))

        mommy.make(
            "small_small_hr.AnnualLeave",
            staff=staffprofile,
            year=2017,
            leave_type=Leave.REGULAR,
            carried_over_days=12,
        )

        data = {
            "staff": staffprofile.id,
            "leave_type": Leave.REGULAR,
            "start": start,
            "end": end,
            "review_reason": "Need a break",
        }

        form = ApplyLeaveForm(data=data)
        self.assertTrue(form.is_valid())
        leave = form.save()
        self.assertEqual(staffprofile, leave.staff)
        self.assertEqual(Leave.REGULAR, leave.leave_type)
        self.assertEqual(start, leave.start)
        self.assertEqual(end, leave.end)
        self.assertEqual(timedelta(days=5).days, (leave.end - leave.start).days)
        self.assertEqual("Need a break", leave.review_reason)
        self.assertEqual(Leave.PENDING, leave.review_status)

    @override_settings(
        SSHR_DEFAULT_TIME=7,
        SSHR_ALLOW_OVERSUBSCRIBE=True,
        SSHR_DAY_LEAVE_VALUES={
            1: 1,  # Monday
            2: 1,  # Tuesday
            3: 1,  # Wednesday
            4: 1,  # Thursday
            5: 1,  # Friday
            6: 1,  # Saturday
            7: 1,  # Sunday
        },
    )
    def test_leave_oversubscribe(self):
        """Test leave oversubscribe works as expected."""
        user = mommy.make("auth.User", first_name="Bob", last_name="Ndoe")
        staffprofile = mommy.make("small_small_hr.StaffProfile", user=user)
        staffprofile.leave_days = 21
        staffprofile.sick_days = 10
        staffprofile.save()

        request = self.factory.get("/")
        request.session = {}
        request.user = AnonymousUser()

        # 40 days of leave
        start = datetime(2017, 6, 1, 7, 0, 0, tzinfo=pytz.timezone(settings.TIME_ZONE))
        end = datetime(2017, 7, 10, 7, 0, 0, tzinfo=pytz.timezone(settings.TIME_ZONE))

        mommy.make(
            "small_small_hr.AnnualLeave",
            staff=staffprofile,
            year=2017,
            leave_type=Leave.REGULAR,
            carried_over_days=0,
        )

        data = {
            "staff": staffprofile.id,
            "leave_type": Leave.REGULAR,
            "start": start,
            "end": end,
            "review_reason": "Mini retirement",
        }

        form = ApplyLeaveForm(data=data)
        self.assertTrue(form.is_valid())
        leave = form.save()

        # make it approved
        obj_type = ContentType.objects.get_for_model(leave)
        review = ModelReview.objects.get(content_type=obj_type, object_id=leave.id)
        review.review_status = ModelReview.APPROVED
        review.save()
        leave.refresh_from_db()

        self.assertEqual(staffprofile, leave.staff)
        self.assertEqual(Leave.REGULAR, leave.leave_type)
        self.assertEqual(start, leave.start)
        self.assertEqual(end, leave.end)
        self.assertEqual(timedelta(days=39).days, (leave.end - leave.start).days)
        self.assertEqual("Mini retirement", leave.review_reason)
        self.assertEqual(Leave.APPROVED, leave.review_status)
        self.assertEqual(
            40,
            get_taken_leave_days(
                staffprofile, Leave.APPROVED, Leave.REGULAR, 2017, 2017
            ),
        )
        self.assertEqual(-19, staffprofile.get_available_leave_days(year=2017))

    @override_settings(
        SSHR_DEFAULT_TIME=7,
        SSHR_ALLOW_OVERSUBSCRIBE=False,
        SSHR_DAY_LEAVE_VALUES={
            1: 1,  # Monday
            2: 1,  # Tuesday
            3: 1,  # Wednesday
            4: 1,  # Thursday
            5: 1,  # Friday
            6: 1,  # Saturday
            7: 1,  # Sunday
        },
    )
    def test_leave_oversubscribe_off(self):
        """Test leave oversubscribe when SSHR_ALLOW_OVERSUBSCRIBE is False."""
        user = mommy.make("auth.User", first_name="Bob", last_name="Ndoe")
        staffprofile = mommy.make("small_small_hr.StaffProfile", user=user)
        staffprofile.leave_days = 21
        staffprofile.sick_days = 10
        staffprofile.save()

        request = self.factory.get("/")
        request.session = {}
        request.user = AnonymousUser()

        # 40 days of leave
        start = datetime(2017, 6, 1, 7, 0, 0, tzinfo=pytz.timezone(settings.TIME_ZONE))
        end = datetime(2017, 7, 10, 7, 0, 0, tzinfo=pytz.timezone(settings.TIME_ZONE))

        mommy.make(
            "small_small_hr.AnnualLeave",
            staff=staffprofile,
            year=2017,
            leave_type=Leave.REGULAR,
            carried_over_days=0,
        )

        data = {
            "staff": staffprofile.id,
            "leave_type": Leave.REGULAR,
            "start": start,
            "end": end,
            "review_reason": "Mini retirement",
        }

        form = ApplyLeaveForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertEqual(2, len(form.errors.keys()))
        self.assertEqual(
            "Not enough leave days. Available leave days are 21.00",
            form.errors["start"][0],
        )
        self.assertEqual(
            "Not enough leave days. Available leave days are 21.00",
            form.errors["end"][0],
        )

    @override_settings(SSHR_DEFAULT_TIME=7)
    def test_one_day_leave(self):
        """Test application for one day leave."""
        user = mommy.make("auth.User", first_name="Bob", last_name="Ndoe")
        staffprofile = mommy.make("small_small_hr.StaffProfile", user=user)
        staffprofile.leave_days = 21
        staffprofile.sick_days = 10
        staffprofile.save()

        request = self.factory.get("/")
        request.session = {}
        request.user = AnonymousUser()

        # 1 day of leave
        start = datetime(2017, 6, 5, 7, 0, 0, tzinfo=pytz.timezone(settings.TIME_ZONE))
        end = datetime(2017, 6, 5, 7, 0, 0, tzinfo=pytz.timezone(settings.TIME_ZONE))

        mommy.make(
            "small_small_hr.AnnualLeave",
            staff=staffprofile,
            year=2017,
            leave_type=Leave.REGULAR,
            carried_over_days=12,
        )

        data = {
            "staff": staffprofile.id,
            "leave_type": Leave.REGULAR,
            "start": start,
            "end": end,
            "review_reason": "Need a break",
        }

        form = ApplyLeaveForm(data=data)
        self.assertTrue(form.is_valid())
        leave = form.save()
        self.assertEqual(staffprofile, leave.staff)
        self.assertEqual(Leave.REGULAR, leave.leave_type)
        self.assertEqual(start, leave.start)
        self.assertEqual(end, leave.end)
        self.assertEqual(timedelta(days=0).days, (leave.end - leave.start).days)
        self.assertEqual("Need a break", leave.review_reason)
        self.assertEqual(Leave.PENDING, leave.review_status)
        self.assertEqual(
            1,
            get_taken_leave_days(
                staffprofile, Leave.PENDING, Leave.REGULAR, 2017, 2017
            ),
        )

    @override_settings(SSHR_DEFAULT_TIME=7)
    def test_leaveform_no_overlap(self):
        """Test LeaveForm no overlap."""
        user = mommy.make("auth.User", first_name="Bob", last_name="Ndoe")
        staffprofile = mommy.make("small_small_hr.StaffProfile", user=user)
        staffprofile.leave_days = 21
        staffprofile.sick_days = 10
        staffprofile.save()

        request = self.factory.get("/")
        request.session = {}
        request.user = AnonymousUser()

        # 6 days of leave
        start = datetime(2017, 6, 5, 7, 0, 0, tzinfo=pytz.timezone(settings.TIME_ZONE))
        end = datetime(2017, 6, 10, 7, 0, 0, tzinfo=pytz.timezone(settings.TIME_ZONE))

        mommy.make(
            "small_small_hr.AnnualLeave",
            staff=staffprofile,
            year=2017,
            leave_type=Leave.REGULAR,
            carried_over_days=12,
        )

        mommy.make(
            "small_small_hr.Leave",
            leave_type=Leave.REGULAR,
            start=start,
            end=end,
            review_status=Leave.APPROVED,
            staff=staffprofile,
        )

        data = {
            "staff": staffprofile.id,
            "leave_type": Leave.REGULAR,
            "start": start,
            "end": end,
            "review_reason": "Need a break",
        }

        form = ApplyLeaveForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertEqual(2, len(form.errors.keys()))
        self.assertEqual(
            "you cannot have overlapping leave days", form.errors["start"][0]
        )
        self.assertEqual(
            "you cannot have overlapping leave days", form.errors["end"][0]
        )

    @override_settings(SSHR_DEFAULT_TIME=7)
    def test_leaveform_admin(self):
        """Test LeaveForm apply for leave."""
        user = mommy.make("auth.User", first_name="Bob", last_name="Ndoe")
        staffprofile = mommy.make("small_small_hr.StaffProfile", user=user)
        staffprofile.leave_days = 21
        staffprofile.sick_days = 10
        staffprofile.save()

        request = self.factory.get("/")
        request.session = {}
        request.user = AnonymousUser()

        # 6 days of leave
        start = datetime(2017, 6, 5, 7, 0, 0, tzinfo=pytz.timezone(settings.TIME_ZONE))
        end = datetime(2017, 6, 10, 7, 0, 0, tzinfo=pytz.timezone(settings.TIME_ZONE))

        mommy.make(
            "small_small_hr.AnnualLeave",
            staff=staffprofile,
            year=2017,
            leave_type=Leave.REGULAR,
            carried_over_days=12,
        )

        data = {
            "staff": staffprofile.id,
            "leave_type": Leave.REGULAR,
            "start": start,
            "end": end,
            "review_reason": "Need a break",
            "review_status": Leave.APPROVED,
        }

        form = LeaveForm(data=data)
        self.assertTrue(form.is_valid())
        leave = form.save()
        self.assertEqual(staffprofile, leave.staff)
        self.assertEqual(Leave.REGULAR, leave.leave_type)
        self.assertEqual(start, leave.start)
        self.assertEqual(end, leave.end)
        self.assertEqual(timedelta(days=5).days, (leave.end - leave.start).days)
        self.assertEqual("Need a break", leave.review_reason)
        self.assertEqual(Leave.APPROVED, leave.review_status)

    @override_settings(SSHR_DEFAULT_TIME=7)
    def test_leaveform_process(self):
        """Test LeaveForm process."""
        user = mommy.make("auth.User", first_name="Bob", last_name="Ndoe")
        staffprofile = mommy.make("small_small_hr.StaffProfile", user=user)
        staffprofile.leave_days = 21
        staffprofile.sick_days = 10
        staffprofile.save()

        request = self.factory.get("/")
        request.session = {}
        request.user = AnonymousUser()

        # 6 days of leave
        start = datetime(2017, 6, 5, 7, 0, 0, tzinfo=pytz.timezone(settings.TIME_ZONE))
        end = datetime(2017, 6, 10, 7, 0, 0, tzinfo=pytz.timezone(settings.TIME_ZONE))

        mommy.make(
            "small_small_hr.AnnualLeave",
            staff=staffprofile,
            year=2017,
            leave_type=Leave.REGULAR,
            carried_over_days=4,
        )

        data = {
            "staff": staffprofile.id,
            "leave_type": Leave.REGULAR,
            "start": start,
            "end": end,
            "review_reason": "Need a break",
            "review_status": Leave.REJECTED,
        }

        form = LeaveForm(data=data)
        self.assertTrue(form.is_valid())
        leave = form.save()
        self.assertEqual(staffprofile, leave.staff)
        self.assertEqual(Leave.REGULAR, leave.leave_type)
        self.assertEqual(start, leave.start)
        self.assertEqual(end, leave.end)
        self.assertEqual(timedelta(days=5).days, (leave.end - leave.start).days)
        self.assertEqual("Need a break", leave.review_reason)
        self.assertEqual(Leave.REJECTED, leave.review_status)

    @override_settings(SSHR_DEFAULT_TIME=7)
    def test_leaveform_process_with_overlap(self):
        """Test LeaveForm process works even if leave object exists."""
        user = mommy.make("auth.User", first_name="Bob", last_name="Ndoe")
        staffprofile = mommy.make("small_small_hr.StaffProfile", user=user)
        staffprofile.leave_days = 21
        staffprofile.sick_days = 10
        staffprofile.save()

        request = self.factory.get("/")
        request.session = {}
        request.user = AnonymousUser()

        # 6 days of leave
        start = datetime(2017, 6, 5, 7, 0, 0, tzinfo=pytz.timezone(settings.TIME_ZONE))
        end = datetime(2017, 6, 10, 7, 0, 0, tzinfo=pytz.timezone(settings.TIME_ZONE))

        # make sure leave obj already exists for said dates
        mommy.make(
            "small_small_hr.Leave",
            staff=staffprofile,
            start=start,
            end=end,
            leave_type=Leave.REGULAR,
            review_status=Leave.APPROVED,
        )

        mommy.make(
            "small_small_hr.AnnualLeave",
            staff=staffprofile,
            year=2017,
            leave_type=Leave.REGULAR,
            carried_over_days=4,
        )

        data = {
            "staff": staffprofile.id,
            "leave_type": Leave.REGULAR,
            "start": start,
            "end": end,
            "review_reason": "Need a break",
            "review_status": Leave.REJECTED,
        }

        form = LeaveForm(data=data)
        self.assertTrue(form.is_valid())
        leave = form.save()
        self.assertEqual(staffprofile, leave.staff)
        self.assertEqual(Leave.REGULAR, leave.leave_type)
        self.assertEqual(start, leave.start)
        self.assertEqual(end, leave.end)
        self.assertEqual(timedelta(days=5).days, (leave.end - leave.start).days)
        self.assertEqual("Need a break", leave.review_reason)
        self.assertEqual(Leave.REJECTED, leave.review_status)

    @override_settings(SSHR_DEFAULT_TIME=7)
    def test_sickleave_apply(self):
        """Test LeaveForm apply for sick leave."""
        user = mommy.make("auth.User", first_name="Bob", last_name="Ndoe")
        staffprofile = mommy.make("small_small_hr.StaffProfile", user=user)
        staffprofile.leave_days = 21
        staffprofile.sick_days = 10
        staffprofile.save()

        request = self.factory.get("/")
        request.session = {}
        request.user = AnonymousUser()

        # 6 days of leave
        start = datetime(2017, 6, 5, 7, 0, 0, tzinfo=pytz.timezone(settings.TIME_ZONE))
        end = datetime(2017, 6, 10, 7, 0, 0, tzinfo=pytz.timezone(settings.TIME_ZONE))

        mommy.make(
            "small_small_hr.AnnualLeave",
            staff=staffprofile,
            year=2017,
            leave_type=Leave.SICK,
            carried_over_days=4,
        )

        data = {
            "staff": staffprofile.id,
            "leave_type": Leave.SICK,
            "start": start,
            "end": end,
            "review_reason": "Need a break",
        }

        form = ApplyLeaveForm(data=data)
        self.assertTrue(form.is_valid())
        leave = form.save()
        self.assertEqual(staffprofile, leave.staff)
        self.assertEqual(Leave.SICK, leave.leave_type)
        self.assertEqual(start, leave.start)
        self.assertEqual(end, leave.end)
        self.assertEqual(timedelta(days=5).days, (leave.end - leave.start).days)
        self.assertEqual("Need a break", leave.review_reason)
        self.assertEqual(Leave.PENDING, leave.review_status)

    @override_settings(SSHR_DEFAULT_TIME=7)
    def test_sickleave_process(self):
        """Test LeaveForm process sick leave."""
        user = mommy.make("auth.User", first_name="Bob", last_name="Ndoe")
        staffprofile = mommy.make("small_small_hr.StaffProfile", user=user)
        staffprofile.leave_days = 21
        staffprofile.sick_days = 10
        staffprofile.save()

        request = self.factory.get("/")
        request.session = {}
        request.user = AnonymousUser()

        # 6 days of leave
        start = datetime(2017, 6, 5, 7, 0, 0, tzinfo=pytz.timezone(settings.TIME_ZONE))
        end = datetime(2017, 6, 10, 7, 0, 0, tzinfo=pytz.timezone(settings.TIME_ZONE))

        mommy.make(
            "small_small_hr.AnnualLeave",
            staff=staffprofile,
            year=2017,
            leave_type=Leave.SICK,
            carried_over_days=4,
        )

        data = {
            "staff": staffprofile.id,
            "leave_type": Leave.SICK,
            "start": start,
            "end": end,
            "review_reason": "Need a break",
            "review_status": Leave.REJECTED,
        }

        form = LeaveForm(data=data)
        self.assertTrue(form.is_valid())
        leave = form.save()
        self.assertEqual(staffprofile, leave.staff)
        self.assertEqual(Leave.SICK, leave.leave_type)
        self.assertEqual(start, leave.start)
        self.assertEqual(end, leave.end)
        self.assertEqual(timedelta(days=5).days, (leave.end - leave.start).days)
        self.assertEqual("Need a break", leave.review_reason)
        self.assertEqual(Leave.REJECTED, leave.review_status)

    def test_leaveform_start_end(self):
        """Test start and end."""
        user = mommy.make("auth.User", first_name="Bob", last_name="Ndoe")
        staffprofile = mommy.make("small_small_hr.StaffProfile", user=user)
        staffprofile.leave_days = 21
        staffprofile.sick_days = 10
        staffprofile.save()

        request = self.factory.get("/")
        request.session = {}
        request.user = AnonymousUser()

        # 6 days of leave
        start = datetime(2017, 6, 5, 0, 0, 0, tzinfo=pytz.timezone(settings.TIME_ZONE))
        end = datetime(2017, 6, 1, 0, 0, 0, tzinfo=pytz.timezone(settings.TIME_ZONE))

        mommy.make(
            "small_small_hr.AnnualLeave",
            staff=staffprofile,
            year=2017,
            leave_type=Leave.SICK,
            carried_over_days=4,
        )

        data = {
            "staff": staffprofile.id,
            "leave_type": Leave.SICK,
            "start": start,
            "end": end,
            "review_reason": "Need a break",
        }

        form = LeaveForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertEqual(1, len(form.errors.keys()))
        self.assertEqual("end must be greater than start", form.errors["end"][0])

        # end year and start year must be the same

        end = datetime(2018, 6, 1, 0, 0, 0, tzinfo=pytz.timezone(settings.TIME_ZONE))

        data2 = {
            "staff": staffprofile.id,
            "leave_type": Leave.SICK,
            "start": start,
            "end": end,
            "review_reason": "Need a break",
        }

        form2 = LeaveForm(data=data2)
        self.assertFalse(form2.is_valid())
        self.assertEqual(2, len(form2.errors.keys()))
        self.assertEqual(
            "start and end must be from the same year", form2.errors["start"][0]
        )
        self.assertEqual(
            "start and end must be from the same year", form2.errors["end"][0]
        )

    @override_settings(SSHR_ALLOW_OVERSUBSCRIBE=False)
    def test_leaveform_max_days(self):
        """Test leave days sufficient."""
        user = mommy.make("auth.User", first_name="Bob", last_name="Ndoe")
        staffprofile = mommy.make("small_small_hr.StaffProfile", user=user)
        staffprofile.leave_days = 21
        staffprofile.sick_days = 10
        staffprofile.save()

        request = self.factory.get("/")
        request.session = {}
        request.user = AnonymousUser()

        # 6 days of leave
        start = datetime(2017, 6, 5, 0, 0, 0, tzinfo=pytz.timezone(settings.TIME_ZONE))
        end = datetime(2017, 7, 10, 0, 0, 0, tzinfo=pytz.timezone(settings.TIME_ZONE))

        mommy.make(
            "small_small_hr.AnnualLeave",
            staff=staffprofile,
            year=2017,
            leave_type=Leave.REGULAR,
            allowed_days=21,
        )

        data = {
            "staff": staffprofile.id,
            "leave_type": Leave.REGULAR,
            "start": start,
            "end": end,
            "review_reason": "Need a break",
        }

        form = LeaveForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertEqual(2, len(form.errors.keys()))
        self.assertEqual(
            "Not enough leave days. Available leave days are 21.00",
            form.errors["start"][0],
        )
        self.assertEqual(
            "Not enough leave days. Available leave days are 21.00",
            form.errors["end"][0],
        )

    @override_settings(SSHR_ALLOW_OVERSUBSCRIBE=False)
    def test_leaveform_max_sick_days(self):
        """Test sick days sufficient."""
        user = mommy.make("auth.User", first_name="Bob", last_name="Ndoe")
        staffprofile = mommy.make("small_small_hr.StaffProfile", user=user)
        staffprofile.leave_days = 21
        staffprofile.sick_days = 10
        staffprofile.save()

        request = self.factory.get("/")
        request.session = {}
        request.user = AnonymousUser()

        # 6 days of leave
        start = datetime(2017, 6, 5, 0, 0, 0, tzinfo=pytz.timezone(settings.TIME_ZONE))
        end = datetime(2017, 6, 20, 0, 0, 0, tzinfo=pytz.timezone(settings.TIME_ZONE))

        mommy.make(
            "small_small_hr.AnnualLeave",
            staff=staffprofile,
            year=2017,
            leave_type=Leave.SICK,
            carried_over_days=0,
            allowed_days=10,
        )

        data = {
            "staff": staffprofile.id,
            "leave_type": Leave.SICK,
            "start": start,
            "end": end,
            "review_reason": "Need a break",
        }

        form = LeaveForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertEqual(2, len(form.errors.keys()))
        self.assertEqual(
            "Not enough sick days. Available sick days are 10.00",
            form.errors["start"][0],
        )
        self.assertEqual(
            "Not enough sick days. Available sick days are 10.00", form.errors["end"][0]
        )

    @override_settings(PRIVATE_STORAGE_ROOT="/tmp/")
    def test_staffdocumentform(self):
        """Test StaffDocumentForm."""
        user = mommy.make("auth.User", first_name="Bob", last_name="Ndoe")
        staffprofile = mommy.make("small_small_hr.StaffProfile", user=user)

        request = self.factory.get("/")
        request.session = {}
        request.user = AnonymousUser()

        path = os.path.join(BASE_DIR, "tests", "fixtures", "contract.pdf")

        with open(path, "r+b") as contract_file:
            data = {
                "staff": staffprofile.id,
                "name": "Employment Contract",
                "description": "This is the employment contract!",
                "file": contract_file,
                "public": True,
            }

            file_dict = {
                "file": SimpleUploadedFile(
                    name=contract_file.name,
                    content=contract_file.read(),
                    content_type="application/pdf",
                )
            }

            form = StaffDocumentForm(data, file_dict)

            self.assertTrue(form.is_valid())
            doc = form.save()

            self.assertEqual(staffprofile, doc.staff)
            self.assertEqual("Employment Contract", doc.name)
            self.assertEqual(True, doc.public)
            self.assertEqual("This is the employment contract!", doc.description)

        with open(path, "r+b") as contract_file:
            self.assertTrue(contract_file.read(), doc.file.read())

        # on updating it, check that file is not required
        data2 = {
            "staff": staffprofile.id,
            "name": "Employment Contract",
            "description": "This is the employment contract!",
        }
        form2 = StaffDocumentForm(data=data2, instance=doc, request=request)
        self.assertTrue(form2.is_valid())

    @override_settings(PRIVATE_STORAGE_ROOT="/tmp/")
    def test_userstaffdocumentform(self):
        """Test UserStaffDocumentForm."""
        user = mommy.make("auth.User", first_name="Bob", last_name="Ndoe")
        staffprofile = mommy.make("small_small_hr.StaffProfile", user=user)

        request = self.factory.get("/")
        request.session = {}
        request.user = user

        path = os.path.join(BASE_DIR, "tests", "fixtures", "contract.pdf")

        with open(path, "r+b") as contract_file:
            data = {
                "staff": staffprofile.id,
                "name": "Employment Contract",
                "description": "This is the employment contract!",
                "file": contract_file,
            }

            file_dict = {
                "file": SimpleUploadedFile(
                    name=contract_file.name,
                    content=contract_file.read(),
                    content_type="application/pdf",
                )
            }

            form = UserStaffDocumentForm(data=data, files=file_dict, request=request)

            self.assertTrue(form.is_valid())
            doc = form.save()

            self.assertEqual(staffprofile, doc.staff)
            self.assertEqual("Employment Contract", doc.name)
            self.assertEqual(False, doc.public)
            self.assertEqual("This is the employment contract!", doc.description)

        with open(path, "r+b") as contract_file:
            self.assertTrue(contract_file.read(), doc.file.read())

        # on updating it, check that file is not required
        data2 = {
            "staff": staffprofile.id,
            "name": "Employment Contract",
            "description": "This is the employment contract!",
        }
        form2 = StaffDocumentForm(data=data2, instance=doc, request=request)
        self.assertTrue(form2.is_valid())

    def test_staff_profile_user_form(self):
        """Test StaffProfileUserForm."""
        user = mommy.make("auth.User")
        staffprofile = mommy.make("small_small_hr.StaffProfile", user=user)

        request = self.factory.get("/")
        request.session = {}
        request.user = AnonymousUser()

        path = os.path.join(BASE_DIR, "tests", "fixtures", "profile.png")

        with open(path, "r+b") as image_file:
            data = {
                "first_name": "Bob",
                "last_name": "Mbugua",
                "id_number": "123456789",
                "sex": StaffProfile.MALE,
                "nhif": "111111",
                "nssf": "222222",
                "pin_number": "A0000000Y",
                "emergency_contact_name": "Bob Father",
                "emergency_contact_relationship": "Father",
                "emergency_contact_number": "+254722111111",
                "phone": "+254722111111",
                "address": "This is the address.",
                "birthday": "1996-01-27",
                "image": image_file,
            }

            file_dict = {
                "image": SimpleUploadedFile(
                    name=image_file.name,
                    content=image_file.read(),
                    content_type="image/png",
                )
            }

            form = StaffProfileUserForm(
                data=data, instance=staffprofile, request=request, files=file_dict
            )
            self.assertTrue(form.is_valid())
            form.save()

            user.refresh_from_db()

            self.assertEqual("Bob Mbugua", user.staffprofile.get_name())
            self.assertEqual(StaffProfile.MALE, staffprofile.sex)
            self.assertEqual("+254722111111", staffprofile.phone.as_e164)

            self.assertEqual("This is the address.", staffprofile.address)
            self.assertEqual("1996-01-27", str(staffprofile.birthday))

            self.assertEqual("123456789", staffprofile.data["id_number"])
            self.assertEqual("111111", staffprofile.data["nhif"])
            self.assertEqual("222222", staffprofile.data["nssf"])
            self.assertEqual("A0000000Y", staffprofile.data["pin_number"])
            self.assertEqual("Bob Father", staffprofile.data["emergency_contact_name"])
            self.assertEqual(
                "Father", staffprofile.data["emergency_contact_relationship"]
            )
            self.assertEqual(
                "+254722111111", staffprofile.data["emergency_contact_number"]
            )

        with open(path, "r+b") as image_file:
            self.assertTrue(image_file.read(), staffprofile.image.read())

    def test_staffprofile_user_form_no_image(self):
        """Test StaffProfileUserForm image not required on update."""
        user = mommy.make("auth.User")
        staffprofile = mommy.make("small_small_hr.StaffProfile", user=user)

        request = self.factory.get("/")
        request.session = {}
        request.user = AnonymousUser()

        path = os.path.join(BASE_DIR, "tests", "fixtures", "profile.png")

        with open(path, "r+b") as image_file:
            data = {
                "first_name": "Bob",
                "last_name": "Mbugua",
                "id_number": "123456789",
                "sex": StaffProfile.MALE,
                "nhif": "111111",
                "nssf": "222222",
                "pin_number": "A0000000Y",
                "emergency_contact_name": "Bob Father",
                "emergency_contact_relationship": "Father",
                "emergency_contact_number": "+254722111111",
                "phone": "+254722111111",
                "address": "This is the address.",
                "birthday": "1996-01-27",
                "image": image_file,
            }

            file_dict = {
                "image": SimpleUploadedFile(
                    name=image_file.name,
                    content=image_file.read(),
                    content_type="image/png",
                )
            }

            form = StaffProfileUserForm(
                data=data, instance=staffprofile, request=request, files=file_dict
            )
            self.assertTrue(form.is_valid())
            form.save()

        staffprofile.refresh_from_db()
        data2 = {
            "first_name": "Bobbie",
            "last_name": "B",
            "id_number": 6666,
        }

        form2 = StaffProfileUserForm(data=data2, instance=staffprofile, request=request)
        self.assertTrue(form2.is_valid())
        form2.save()
        staffprofile.refresh_from_db()
        self.assertEqual("Bobbie B", user.staffprofile.get_name())

    def test_staff_profile_admin_create_form(self):
        """Test StaffProfileAdminCreateForm."""
        user = mommy.make("auth.User")

        manager = mommy.make("auth.User", username="manager")
        managerprofile = mommy.make("small_small_hr.StaffProfile", user=manager)

        request = self.factory.get("/")
        request.session = {}
        request.user = AnonymousUser()

        path = os.path.join(BASE_DIR, "tests", "fixtures", "profile.png")

        with open(path, "r+b") as image_file:
            data = {
                "user": user.id,
                "first_name": "Bob",
                "last_name": "Mbugua",
                "id_number": "123456789",
                "sex": StaffProfile.MALE,
                "nhif": "111111",
                "nssf": "222222",
                "pin_number": "A0000000Y",
                "emergency_contact_name": "Bob Father",
                "emergency_contact_number": "+254722111111",
                "phone": "+254722111111",
                "address": "This is the address.",
                "birthday": "1996-01-27",
                "leave_days": 21,
                "sick_days": 9,
                "overtime_allowed": True,
                "start_date": "2017-09-25",
                "end_date": "2018-12-31",
                "image": image_file,
                "supervisor": managerprofile.pk,
            }

            file_dict = {
                "image": SimpleUploadedFile(
                    name=image_file.name,
                    content=image_file.read(),
                    content_type="image/png",
                )
            }

            form = StaffProfileAdminCreateForm(
                data=data, files=file_dict, request=request
            )
            self.assertTrue(form.is_valid())
            staffprofile = form.save()

            user.refresh_from_db()

            self.assertEqual("Bob Mbugua", user.staffprofile.get_name())
            self.assertEqual(StaffProfile.MALE, staffprofile.sex)
            self.assertEqual("+254722111111", staffprofile.phone.as_e164)
            self.assertEqual(21, staffprofile.leave_days)
            self.assertEqual(9, staffprofile.sick_days)
            self.assertEqual(True, staffprofile.overtime_allowed)
            self.assertEqual(managerprofile, staffprofile.supervisor)

            self.assertEqual("This is the address.", staffprofile.address)
            self.assertEqual("1996-01-27", str(staffprofile.birthday))
            self.assertEqual("2017-09-25", str(staffprofile.start_date))
            self.assertEqual("2018-12-31", str(staffprofile.end_date))

            self.assertEqual("123456789", staffprofile.data["id_number"])
            self.assertEqual("111111", staffprofile.data["nhif"])
            self.assertEqual("222222", staffprofile.data["nssf"])
            self.assertEqual("A0000000Y", staffprofile.data["pin_number"])
            self.assertEqual("Bob Father", staffprofile.data["emergency_contact_name"])
            self.assertEqual(
                "+254722111111", staffprofile.data["emergency_contact_number"]
            )

        with open(path, "r+b") as image_file:
            self.assertTrue(image_file.read(), staffprofile.image.read())

    def test_staff_profile_admin_form(self):
        """Test StaffProfileAdminForm."""
        managerprofile = self.manager_profile
        user = self.user
        staffprofile = self.staffprofile

        request = self.factory.get("/")
        request.session = {}
        request.user = AnonymousUser()

        path = os.path.join(BASE_DIR, "tests", "fixtures", "profile.png")

        with open(path, "r+b") as image_file:
            data = {
                "user": user.id,
                "first_name": "Bob",
                "last_name": "Mbugua",
                "id_number": "123456789",
                "sex": StaffProfile.MALE,
                "nhif": "111111",
                "nssf": "222222",
                "pin_number": "A0000000Y",
                "emergency_contact_name": "Bob Father",
                "emergency_contact_number": "+254722111111",
                "phone": "+254722111111",
                "address": "This is the address.",
                "birthday": "1996-01-27",
                "leave_days": 21,
                "sick_days": 9,
                "overtime_allowed": True,
                "start_date": "2017-09-25",
                "end_date": "2018-12-31",
                "image": image_file,
                "supervisor": managerprofile.pk,
            }

            file_dict = {
                "image": SimpleUploadedFile(
                    name=image_file.name,
                    content=image_file.read(),
                    content_type="image/png",
                )
            }

            form = StaffProfileAdminForm(
                data=data, instance=staffprofile, request=request, files=file_dict
            )
            self.assertTrue(form.is_valid())
            form.save()

            user.refresh_from_db()

            self.assertEqual("Bob Mbugua", user.staffprofile.get_name())
            self.assertEqual(StaffProfile.MALE, staffprofile.sex)
            self.assertEqual("+254722111111", staffprofile.phone.as_e164)
            self.assertEqual(21, staffprofile.leave_days)
            self.assertEqual(9, staffprofile.sick_days)
            self.assertEqual(True, staffprofile.overtime_allowed)
            self.assertEqual(managerprofile, staffprofile.supervisor)

            self.assertEqual("This is the address.", staffprofile.address)
            self.assertEqual("1996-01-27", str(staffprofile.birthday))
            self.assertEqual("2017-09-25", str(staffprofile.start_date))
            self.assertEqual("2018-12-31", str(staffprofile.end_date))

            self.assertEqual("123456789", staffprofile.data["id_number"])
            self.assertEqual("111111", staffprofile.data["nhif"])
            self.assertEqual("222222", staffprofile.data["nssf"])
            self.assertEqual("A0000000Y", staffprofile.data["pin_number"])
            self.assertEqual("Bob Father", staffprofile.data["emergency_contact_name"])
            self.assertEqual(
                "+254722111111", staffprofile.data["emergency_contact_number"]
            )

        with open(path, "r+b") as image_file:
            self.assertTrue(image_file.read(), staffprofile.image.read())

    def test_staffprofile_admin_form_no_image(self):
        """Test StaffProfileAdminForm image not required when editting."""
        user = mommy.make("auth.User")
        staffprofile = mommy.make("small_small_hr.StaffProfile", user=user)

        request = self.factory.get("/")
        request.session = {}
        request.user = AnonymousUser()

        path = os.path.join(BASE_DIR, "tests", "fixtures", "profile.png")

        with open(path, "r+b") as image_file:
            data = {
                "user": user.id,
                "first_name": "Bob",
                "last_name": "Mbugua",
                "id_number": "123456789",
                "sex": StaffProfile.MALE,
                "nhif": "111111",
                "nssf": "222222",
                "pin_number": "A0000000Y",
                "emergency_contact_name": "Bob Father",
                "emergency_contact_number": "+254722111111",
                "phone": "+254722111111",
                "address": "This is the address.",
                "birthday": "1996-01-27",
                "leave_days": 21,
                "sick_days": 9,
                "overtime_allowed": True,
                "start_date": "2017-09-25",
                "end_date": "2018-12-31",
                "image": image_file,
            }

            file_dict = {
                "image": SimpleUploadedFile(
                    name=image_file.name,
                    content=image_file.read(),
                    content_type="image/png",
                )
            }

            form = StaffProfileAdminForm(
                data=data, instance=staffprofile, request=request, files=file_dict
            )
            self.assertTrue(form.is_valid())
            form.save()

        staffprofile.refresh_from_db()
        data2 = {
            "user": user.id,
            "first_name": "Bobbie",
            "last_name": "B",
            "id_number": 6666,
        }

        form2 = StaffProfileAdminForm(
            data=data2, instance=staffprofile, request=request
        )
        self.assertTrue(form2.is_valid())
        form2.save()
        staffprofile.refresh_from_db()
        self.assertEqual("Bobbie B", user.staffprofile.get_name())

    def test_staffprofile_unique_pin_number(self):
        """Test unique pin_number."""
        user = mommy.make("auth.User", first_name="Bob", last_name="Ndoe")
        staffprofile = mommy.make("small_small_hr.StaffProfile", user=user)
        staffprofile.data["id_number"] = "123456789"
        staffprofile.data["pin_number"] = "123456789"
        staffprofile.save()

        user2 = mommy.make("auth.User", first_name="Kyle", last_name="Ndoe")
        staffprofile2 = mommy.make("small_small_hr.StaffProfile", user=user2)
        staffprofile2.data["id_number"] = "9999999"
        staffprofile2.save()

        request = self.factory.get("/")
        request.session = {}
        request.user = AnonymousUser()

        data = StaffProfileSerializer(staffprofile2).data
        data["pin_number"] = "123456789"

        form = StaffProfileAdminForm(data=data, instance=staffprofile2, request=request)
        self.assertFalse(form.is_valid())
        self.assertEqual(1, len(form.errors.keys()))
        self.assertEqual(
            "This PIN number is already in use.", form.errors["pin_number"][0]
        )

    def test_staffprofile_unique_id_number(self):
        """Test unique id_number."""
        user = mommy.make("auth.User", first_name="Bob", last_name="Ndoe")
        staffprofile = mommy.make("small_small_hr.StaffProfile", user=user)
        staffprofile.data["id_number"] = "123456789"
        staffprofile.save()

        user2 = mommy.make("auth.User", first_name="Kyle", last_name="Ndoe")
        staffprofile2 = mommy.make("small_small_hr.StaffProfile", user=user2)
        staffprofile2.save()

        request = self.factory.get("/")
        request.session = {}
        request.user = AnonymousUser()

        data = StaffProfileSerializer(staffprofile2).data
        data["id_number"] = "123456789"

        form = StaffProfileAdminForm(data=data, instance=staffprofile2, request=request)
        self.assertFalse(form.is_valid())
        self.assertEqual(1, len(form.errors.keys()))
        self.assertEqual(
            "This id number is already in use.", form.errors["id_number"][0]
        )

    def test_staffprofile_unique_nssf(self):
        """Test unique NSSF."""
        user = mommy.make("auth.User", first_name="Bob", last_name="Ndoe")
        staffprofile = mommy.make("small_small_hr.StaffProfile", user=user)
        staffprofile.data["id_number"] = "123456789"
        staffprofile.data["nssf"] = "123456789"
        staffprofile.save()

        user2 = mommy.make("auth.User", first_name="Kyle", last_name="Ndoe")
        staffprofile2 = mommy.make("small_small_hr.StaffProfile", user=user2)
        staffprofile2.data["id_number"] = "9999999"
        staffprofile2.save()

        request = self.factory.get("/")
        request.session = {}
        request.user = AnonymousUser()

        data = StaffProfileSerializer(staffprofile2).data
        data["nssf"] = "123456789"

        form = StaffProfileAdminForm(data=data, instance=staffprofile2, request=request)
        self.assertFalse(form.is_valid())
        self.assertEqual(1, len(form.errors.keys()))
        self.assertEqual("This NSSF number is already in use.", form.errors["nssf"][0])

    def test_staffprofile_unique_nhif(self):
        """Test unique NHIF."""
        user = mommy.make("auth.User", first_name="Bob", last_name="Ndoe")
        staffprofile = mommy.make("small_small_hr.StaffProfile", user=user)
        staffprofile.data["id_number"] = "123456789"
        staffprofile.data["nhif"] = "123456789"
        staffprofile.save()

        user2 = mommy.make("auth.User", first_name="Kyle", last_name="Ndoe")
        staffprofile2 = mommy.make("small_small_hr.StaffProfile", user=user2)
        staffprofile2.data["id_number"] = "9999999"
        staffprofile2.save()

        request = self.factory.get("/")
        request.session = {}
        request.user = AnonymousUser()

        data = StaffProfileSerializer(staffprofile2).data
        data["nhif"] = "123456789"

        form = StaffProfileAdminForm(data=data, instance=staffprofile2, request=request)
        self.assertFalse(form.is_valid())
        self.assertEqual(1, len(form.errors.keys()))
        self.assertEqual("This NHIF number is already in use.", form.errors["nhif"][0])
