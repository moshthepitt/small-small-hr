"""Module to test small_small_hr Emails."""
# pylint: disable=hard-coded-auth-user
from datetime import datetime

from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.core import mail
from django.test import override_settings

import pytz
from freezegun import freeze_time
from model_mommy import mommy
from model_reviews.forms import PerformReview
from model_reviews.models import ModelReview, Reviewer
from snapshottest.django import TestCase

from small_small_hr.forms import ApplyLeaveForm, ApplyOverTimeForm
from small_small_hr.models import Leave, StaffProfile
from small_small_hr.utils import create_annual_leave


@override_settings(ROOT_URLCONF="tests.urls")
class TestEmails(TestCase):
    """Test class for emails."""

    maxDiff = None

    def setUp(self):
        """Set up."""
        self.user = mommy.make(
            "auth.User", first_name="Mosh", last_name="Pitt", email="bob@example.com"
        )
        self.staffprofile = mommy.make("small_small_hr.StaffProfile", user=self.user)
        self.staffprofile.leave_days = 17
        self.staffprofile.sick_days = 9
        self.staffprofile.save()
        self.staffprofile.refresh_from_db()

        create_annual_leave(self.staffprofile, 2017, Leave.REGULAR)

        StaffProfile.objects.rebuild()

        hr_group = mommy.make("auth.Group", name=settings.SSHR_ADMIN_USER_GROUP_NAME)
        self.boss = mommy.make(
            "auth.User", first_name="Mother", last_name="Hen", email="hr@example.com"
        )
        self.boss.groups.add(hr_group)

    @freeze_time("June 1st, 2017")
    def test_leave_emails(self):
        """Test Leave emails."""
        # apply for leave
        start = datetime(2017, 6, 5, 7, 0, 0, tzinfo=pytz.timezone(settings.TIME_ZONE))
        end = datetime(2017, 6, 10, 7, 0, 0, tzinfo=pytz.timezone(settings.TIME_ZONE))
        data = {
            "staff": self.staffprofile.id,
            "leave_type": Leave.REGULAR,
            "start": start,
            "end": end,
            "review_reason": "Need a break",
        }
        form = ApplyLeaveForm(data=data)
        self.assertTrue(form.is_valid())
        leave = form.save()

        obj_type = ContentType.objects.get_for_model(leave)
        # Hard code the pk for the snapshot test
        # empty the test outbox so that we don't deal with the old review's emails
        mail.outbox = []
        ModelReview.objects.get(content_type=obj_type, object_id=leave.id).delete()
        review = mommy.make(
            "model_reviews.ModelReview",
            content_type=obj_type,
            object_id=leave.id,
            id=1338,
        )
        reviewer = Reviewer.objects.get(review=review, user=self.boss)

        self.assertEqual(
            "Mosh Pitt requested time off on 05 Jun to 10 Jun", mail.outbox[0].subject
        )
        self.assertEqual(["Mother Hen <hr@example.com>"], mail.outbox[0].to)
        self.assertMatchSnapshot(mail.outbox[0].body)
        self.assertMatchSnapshot(mail.outbox[0].alternatives[0][0])

        # approve the review
        data = {
            "review": review.pk,
            "reviewer": reviewer.pk,
            "review_status": ModelReview.APPROVED,
        }
        form = PerformReview(data=data)
        self.assertTrue(form.is_valid())
        form.save()
        self.assertEqual(
            "Your time off request of 05 Jun - 10 Jun has a response",
            mail.outbox[1].subject,
        )
        self.assertEqual(["Mosh Pitt <bob@example.com>"], mail.outbox[1].to)
        self.assertMatchSnapshot(mail.outbox[1].body)
        self.assertMatchSnapshot(mail.outbox[1].alternatives[0][0])

        # then reject it
        data = {
            "review": review.pk,
            "reviewer": reviewer.pk,
            "review_status": ModelReview.REJECTED,
        }
        form = PerformReview(data=data)
        self.assertTrue(form.is_valid())
        form.save()
        self.assertEqual(
            "Your time off request of 05 Jun - 10 Jun has a response",
            mail.outbox[2].subject,
        )
        self.assertEqual(["Mosh Pitt <bob@example.com>"], mail.outbox[2].to)
        self.assertMatchSnapshot(mail.outbox[2].body)
        self.assertMatchSnapshot(mail.outbox[2].alternatives[0][0])

    def test_overtime_emails(self):
        """Test Overtime emails."""
        # apply for overtime
        start = datetime(
            2017, 6, 5, 16, 45, 0, tzinfo=pytz.timezone(settings.TIME_ZONE)
        )
        end = datetime(2017, 6, 5, 21, 30, 0, tzinfo=pytz.timezone(settings.TIME_ZONE))

        data = {
            "staff": self.staffprofile.id,
            "date": start.date(),
            "start": start.time(),
            "end": end.time(),
            "review_reason": "Extra work",
        }

        form = ApplyOverTimeForm(data=data)
        self.assertTrue(form.is_valid())
        overtime = form.save()

        obj_type = ContentType.objects.get_for_model(overtime)
        # Hard code the pk for the snapshot test
        # empty the test outbox so that we don't deal with the old review's emails
        mail.outbox = []
        ModelReview.objects.get(content_type=obj_type, object_id=overtime.id).delete()
        review = mommy.make(
            "model_reviews.ModelReview",
            content_type=obj_type,
            object_id=overtime.id,
            id=1337,
        )
        reviewer = Reviewer.objects.get(review=review, user=self.boss)

        self.assertEqual(
            "Mosh Pitt requested overtime on 05 Jun", mail.outbox[0].subject
        )
        self.assertEqual(["Mother Hen <hr@example.com>"], mail.outbox[0].to)
        self.assertMatchSnapshot(mail.outbox[0].body)
        self.assertMatchSnapshot(mail.outbox[0].alternatives[0][0])

        # approve the overtime
        data = {
            "review": review.pk,
            "reviewer": reviewer.pk,
            "review_status": ModelReview.APPROVED,
        }
        form = PerformReview(data=data)
        self.assertTrue(form.is_valid())
        form.save()
        self.assertEqual(
            "Your overtime request of 05 Jun has a response", mail.outbox[1].subject,
        )
        self.assertEqual(["Mosh Pitt <bob@example.com>"], mail.outbox[1].to)
        self.assertMatchSnapshot(mail.outbox[1].body)
        self.assertMatchSnapshot(mail.outbox[1].alternatives[0][0])

        # then reject it
        data = {
            "review": review.pk,
            "reviewer": reviewer.pk,
            "review_status": ModelReview.REJECTED,
        }
        form = PerformReview(data=data)
        self.assertTrue(form.is_valid())
        form.save()
        self.assertEqual(
            "Your overtime request of 05 Jun has a response", mail.outbox[2].subject,
        )
        self.assertEqual(["Mosh Pitt <bob@example.com>"], mail.outbox[2].to)
        self.assertMatchSnapshot(mail.outbox[2].body)
        self.assertMatchSnapshot(mail.outbox[2].alternatives[0][0])
