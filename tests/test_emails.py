# """Module to test small_small_hr Emails."""
# from datetime import datetime
# from unittest.mock import patch

# from django.conf import settings
# from django.test import TestCase, override_settings

# import pytz
# from model_mommy import mommy

# from small_small_hr.emails import (
#     leave_application_email,
#     leave_processed_email,
#     overtime_application_email,
#     overtime_processed_email,
# )
# from small_small_hr.models import Leave, OverTime


# @override_settings(
#     SSHR_ADMIN_EMAILS=["admin@example.com"],
#     SSHR_ADMIN_LEAVE_EMAILS=["hr@example.com"],
#     SSHR_ADMIN_OVERTIME_EMAILS=["ot@example.com"],
#     SSHR_ADMIN_NAME="mosh",
# )
# class TestEmails(TestCase):
#     """Test class for emails."""

#     def setUp(self):
#         """Set up."""
#         self.user = mommy.make(
#             "auth.User", first_name="Bob", last_name="Ndoe", email="bob@example.com"
#         )
#         self.staffprofile = mommy.make("small_small_hr.StaffProfile", user=self.user)

#     @patch("small_small_hr.emails.send_email")
#     def test_leave_application_email(self, mock):
#         """Test leave_application_email."""
#         start = datetime(2017, 6, 5, 0, 0, 0, tzinfo=pytz.timezone(settings.TIME_ZONE))
#         end = datetime(2017, 6, 10, 0, 0, 0, tzinfo=pytz.timezone(settings.TIME_ZONE))
#         leave = mommy.make(
#             "small_small_hr.Leave",
#             staff=self.staffprofile,
#             start=start,
#             end=end,
#             leave_type=Leave.SICK,
#             review_status=Leave.PENDING,
#         )

#         leave_application_email(leave)

#         mock.assert_called_with(
#             name="mosh",
#             email="hr@example.com",
#             subject="New Leave Application",
#             message="There has been a new leave application.  Please log in to process it.",  # noqa  # pylint: disable=line-too-long
#             obj=leave,
#             template="leave_application",
#             template_path="small_small_hr/email",
#         )

#     @patch("small_small_hr.emails.send_email")
#     def test_leave_processed_email(self, mock):
#         """Test leave_processed_email."""
#         start = datetime(2017, 6, 5, 0, 0, 0, tzinfo=pytz.timezone(settings.TIME_ZONE))
#         end = datetime(2017, 6, 10, 0, 0, 0, tzinfo=pytz.timezone(settings.TIME_ZONE))
#         leave = mommy.make(
#             "small_small_hr.Leave",
#             staff=self.staffprofile,
#             start=start,
#             end=end,
#             leave_type=Leave.SICK,
#             review_status=Leave.APPROVED,
#         )

#         leave_processed_email(leave)

#         mock.assert_called_with(
#             name="Bob Ndoe",
#             email="bob@example.com",
#             subject="Your leave application has been processed",
#             message="You leave application status is Approved.  Log in for more info.",  # noqa  # pylint: disable=line-too-long
#             obj=leave,
#             cc_list=["hr@example.com"],
#             template_path="small_small_hr/email",
#         )

#     @patch("small_small_hr.emails.send_email")
#     def test_overtime_application_email(self, mock):
#         """Test overtime_application_email."""
#         start = datetime(2017, 6, 5, 0, 0, 0, tzinfo=pytz.timezone(settings.TIME_ZONE))
#         end = datetime(2017, 6, 10, 0, 0, 0, tzinfo=pytz.timezone(settings.TIME_ZONE))
#         overtime = mommy.make(
#             "small_small_hr.OverTime",
#             staff=self.staffprofile,
#             start=start,
#             end=end,
#             review_status=OverTime.PENDING,
#         )

#         overtime_application_email(overtime)

#         mock.assert_called_with(
#             name="mosh",
#             email="ot@example.com",
#             subject="New Overtime Application",
#             message="There has been a new overtime application.  Please log in to process it.",  # noqa  # pylint: disable=line-too-long
#             obj=overtime,
#             template="overtime_application",
#             template_path="small_small_hr/email",
#         )

#     @patch("small_small_hr.emails.send_email")
#     def test_overtime_processed_email(self, mock):
#         """Test overtime_processed_email."""
#         start = datetime(2017, 6, 5, 0, 0, 0, tzinfo=pytz.timezone(settings.TIME_ZONE))
#         end = datetime(2017, 6, 10, 0, 0, 0, tzinfo=pytz.timezone(settings.TIME_ZONE))
#         overtime = mommy.make(
#             "small_small_hr.OverTime",
#             staff=self.staffprofile,
#             start=start,
#             end=end,
#             review_status=OverTime.REJECTED,
#         )

#         overtime_processed_email(overtime)

#         mock.assert_called_with(
#             name="Bob Ndoe",
#             email="bob@example.com",
#             subject="Your overtime application has been processed",
#             message="You overtime application status is Rejected.  Log in for more info.",  # noqa  # pylint: disable=line-too-long
#             obj=overtime,
#             cc_list=["ot@example.com"],
#             template_path="small_small_hr/email",
#         )
