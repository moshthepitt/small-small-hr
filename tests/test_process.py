"""Test the leave/overtime application process."""
from datetime import datetime

from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.test import RequestFactory, TestCase

import pytz
from model_mommy import mommy
from model_reviews.forms import PerformReview
from model_reviews.models import ModelReview

from small_small_hr.forms import ApplyLeaveForm
from small_small_hr.models import Leave


class TestProcess(TestCase):  # pylint: disable=too-many-public-methods
    """Test the leave/overtime application process."""

    def setUp(self):
        """Set up test class."""
        self.factory = RequestFactory()

    def test_xxx(self):
        """Test xxx."""
        user = mommy.make("auth.User", first_name="Bob", last_name="Ndoe")
        staffprofile = mommy.make("small_small_hr.StaffProfile", user=user)
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
        # reviewer = Leave.none()
        self.fail()

        # perform the review
        data = {
            "review": review.pk,
            # "reviewer": reviewer.pk,
            "review_status": ModelReview.APPROVED,
        }
        form = PerformReview(data=data)
        self.assertTrue(form.is_valid())
        form.save()
