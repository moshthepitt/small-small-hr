"""Test the leave/overtime application process."""
from datetime import datetime
from unittest.mock import call, patch

from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.test import RequestFactory, TestCase

import pytz
from model_mommy import mommy
from model_reviews.forms import PerformReview
from model_reviews.models import ModelReview, Reviewer

from small_small_hr.forms import ApplyLeaveForm
from small_small_hr.models import Leave, StaffProfile


class TestProcess(TestCase):  # pylint: disable=too-many-public-methods
    """Test the leave/overtime application process."""

    def setUp(self):
        """Set up test class."""
        self.factory = RequestFactory()
        StaffProfile.objects.rebuild()
        hr_group = mommy.make("auth.Group", name=settings.SSHR_ADMIN_USER_GROUP_NAME)
        self.boss = mommy.make(
            "auth.User", first_name="Boss", last_name="Lady", email="boss@example.com"
        )
        self.boss.groups.add(hr_group)

    @patch("model_reviews.emails.send_email")
    def test_review_process(self, mock):  # pylint: disable=too-many-locals
        """Test the review process."""
        manager = mommy.make(
            "auth.User", first_name="Jane", last_name="Ndoe", email="jane@example.com"
        )
        manager_profile = mommy.make("small_small_hr.StaffProfile", user=manager)

        user = mommy.make(
            "auth.User", first_name="Bob", last_name="Ndoe", email="bob@example.com"
        )
        staffprofile = mommy.make("small_small_hr.StaffProfile", user=user)
        staffprofile.supervisor = manager_profile
        staffprofile.leave_days = 21
        staffprofile.sick_days = 10
        staffprofile.save()

        # apply for leave
        start = datetime(2017, 6, 5, 7, 0, 0, tzinfo=pytz.timezone(settings.TIME_ZONE))
        end = datetime(2017, 6, 10, 7, 0, 0, tzinfo=pytz.timezone(settings.TIME_ZONE))
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

        # check that a ModelReview object is created
        obj_type = ContentType.objects.get_for_model(leave)
        self.assertEqual(
            1,
            ModelReview.objects.filter(
                content_type=obj_type, object_id=leave.id
            ).count(),
        )
        review = ModelReview.objects.get(content_type=obj_type, object_id=leave.id)
        self.assertTrue(Leave.PENDING, review.review_status)

        # check that email is sent once to the reviewer
        reviewer = Reviewer.objects.get(review=review, user=manager)
        boss_reviewer = Reviewer.objects.get(review=review, user=self.boss)

        expected_calls = [
            call(
                name="Jane Ndoe",
                email="jane@example.com",
                subject="New Request For Approval",
                message="There has been a new request that needs your attention.",
                obj=review,
                cc_list=None,
                template="leave",
                template_path="small_small_hr/email",
            ),
            call(
                name="Boss Lady",
                email="boss@example.com",
                subject="New Request For Approval",
                message="There has been a new request that needs your attention.",
                obj=review,
                cc_list=None,
                template="leave",
                template_path="small_small_hr/email",
            ),
        ]

        mock.assert_has_calls(expected_calls)

        # approve the review
        data = {
            "review": review.pk,
            "reviewer": reviewer.pk,
            "review_status": ModelReview.APPROVED,
        }
        form = PerformReview(data=data)
        self.assertTrue(form.is_valid())
        form.save()
        review.refresh_from_db()
        leave.refresh_from_db()
        self.assertEqual(ModelReview.APPROVED, review.review_status)
        self.assertEqual(Leave.APPROVED, leave.review_status)

        expected_calls.append(
            call(
                name="Bob Ndoe",
                email="bob@example.com",
                subject="Your request has been processed",
                message="Your request has been processed, please log in to view the status.",  # noqa  # pylint: disable=line-too-long
                obj=review,
                cc_list=None,
                template="leave",
                template_path="small_small_hr/email",
            )
        )
        mock.assert_has_calls(expected_calls)

        # boss rejects it
        data = {
            "review": review.pk,
            "reviewer": boss_reviewer.pk,
            "review_status": ModelReview.REJECTED,
        }
        form = PerformReview(data=data)
        self.assertTrue(form.is_valid())
        form.save()
        review.refresh_from_db()
        leave.refresh_from_db()
        self.assertEqual(ModelReview.REJECTED, review.review_status)
        self.assertEqual(Leave.REJECTED, leave.review_status)

        expected_calls.append(
            call(
                name="Bob Ndoe",
                email="bob@example.com",
                subject="Your request has been processed",
                message="Your request has been processed, please log in to view the status.",  # noqa  # pylint: disable=line-too-long
                obj=review,
                cc_list=None,
                template="leave",
                template_path="small_small_hr/email",
            )
        )
        mock.assert_has_calls(expected_calls)

        self.assertEqual(4, mock.call_count)
