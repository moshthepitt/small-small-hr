"""Module to test small_small_hr Emails."""
from datetime import datetime

from django.conf import settings
from django.core import mail
from django.test import override_settings

import pytz
from freezegun import freeze_time
from model_mommy import mommy
from snapshottest.django import TestCase

from small_small_hr.forms import ApplyLeaveForm
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
        form.save()
        self.assertEqual(
            "Mosh Pitt requested time off on 05 Jun to 10 Jun", mail.outbox[0].subject
        )
        self.assertEqual(["Mother Hen <hr@example.com>"], mail.outbox[0].to)
        self.assertMatchSnapshot(mail.outbox[0].body)
        self.assertMatchSnapshot(mail.outbox[0].alternatives[0][0])
        # import ipdb; ipdb.set_trace()
        # leave = form.save()
        # obj_type = ContentType.objects.get_for_model(leave)
        # review = ModelReview.objects.get(content_type=obj_type, object_id=leave.id)
        # reviewer = Reviewer.objects.get(review=review, user=self.boss)
