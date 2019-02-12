"""
Module to test small_small_hr Emails
"""
from datetime import datetime
from unittest.mock import call, patch

from django.conf import settings
from django.core import mail
from django.test import TestCase, override_settings

import pytz
from model_mommy import mommy

from small_small_hr.emails import (leave_application_email,
                                   leave_processed_email,
                                   overtime_application_email,
                                   overtime_processed_email, send_email)
from small_small_hr.models import Leave, OverTime


@override_settings(
    SSHR_ADMIN_EMAILS=["admin@example.com"],
    SSHR_ADMIN_LEAVE_EMAILS=["hr@example.com"],
    SSHR_ADMIN_OVERTIME_EMAILS=["ot@example.com"],
    SSHR_ADMIN_NAME="mosh"
)
class TestEmails(TestCase):
    """
    Test class for emails
    """

    def setUp(self):
        """
        Set up
        """
        self.user = mommy.make(
            'auth.User', first_name='Bob', last_name='Ndoe',
            email="bob@example.com")
        self.staffprofile = mommy.make(
            'small_small_hr.StaffProfile', user=self.user)

    @patch('small_small_hr.emails.send_email')
    def test_leave_application_email(self, mock):
        """
        Test leave_application_email
        """
        start = datetime(
            2017, 6, 5, 0, 0, 0, tzinfo=pytz.timezone(settings.TIME_ZONE))
        end = datetime(
            2017, 6, 10, 0, 0, 0, tzinfo=pytz.timezone(settings.TIME_ZONE))
        leave = mommy.make(
            'small_small_hr.Leave', staff=self.staffprofile, start=start,
            end=end, leave_type=Leave.SICK,
            status=Leave.PENDING)

        leave_application_email(leave)

        mock.assert_called_with(
            name="mosh",
            email="hr@example.com",
            subject="New Leave Application",
            message="There has been a new leave application.  Please log in to process it.",  # noqa
            obj=leave,
            template="leave_application",
        )

    @patch('small_small_hr.emails.send_email')
    def test_leave_processed_email(self, mock):
        """
        Test leave_processed_email
        """
        start = datetime(
            2017, 6, 5, 0, 0, 0, tzinfo=pytz.timezone(settings.TIME_ZONE))
        end = datetime(
            2017, 6, 10, 0, 0, 0, tzinfo=pytz.timezone(settings.TIME_ZONE))
        leave = mommy.make(
            'small_small_hr.Leave', staff=self.staffprofile, start=start,
            end=end, leave_type=Leave.SICK,
            status=Leave.APPROVED)

        leave_processed_email(leave)

        mock.assert_called_with(
            name="Bob Ndoe",
            email="bob@example.com",
            subject="Your leave application has been processed",
            message="You leave application status is Approved.  Log in for more info.",  # noqa
            obj=leave,
            cc_list=['hr@example.com']
        )

    @patch('small_small_hr.emails.send_email')
    def test_overtime_application_email(self, mock):
        """
        Test overtime_application_email
        """
        start = datetime(
            2017, 6, 5, 0, 0, 0, tzinfo=pytz.timezone(settings.TIME_ZONE))
        end = datetime(
            2017, 6, 10, 0, 0, 0, tzinfo=pytz.timezone(settings.TIME_ZONE))
        overtime = mommy.make(
            'small_small_hr.OverTime', staff=self.staffprofile, start=start,
            end=end, status=OverTime.PENDING)

        overtime_application_email(overtime)

        mock.assert_called_with(
            name="mosh",
            email="ot@example.com",
            subject="New Overtime Application",
            message="There has been a new overtime application.  Please log in to process it.",  # noqa
            obj=overtime,
            template="overtime_application",
        )

    @patch('small_small_hr.emails.send_email')
    def test_overtime_processed_email(self, mock):
        """
        Test overtime_processed_email
        """
        start = datetime(
            2017, 6, 5, 0, 0, 0, tzinfo=pytz.timezone(settings.TIME_ZONE))
        end = datetime(
            2017, 6, 10, 0, 0, 0, tzinfo=pytz.timezone(settings.TIME_ZONE))
        overtime = mommy.make(
            'small_small_hr.OverTime', staff=self.staffprofile, start=start,
            end=end, status=OverTime.REJECTED)

        overtime_processed_email(overtime)

        mock.assert_called_with(
            name="Bob Ndoe",
            email="bob@example.com",
            subject="Your overtime application has been processed",
            message="You overtime application status is Rejected.  Log in for more info.",  # noqa
            obj=overtime,
            cc_list=['ot@example.com']
        )

    def test_send_email(self):
        """
        Test send_email
        """

        message = "The quick brown fox."

        data = {
            'name': 'Bob Munro',
            'email': 'bob@example.com',
            'subject': "I love oov",
            'message': message,
            'cc_list': settings.SSHR_ADMIN_EMAILS
        }

        send_email(**data)

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, 'I love oov')
        self.assertEqual(mail.outbox[0].to, ['Bob Munro <bob@example.com>'])
        self.assertEqual(mail.outbox[0].cc, ['admin@example.com'])
        self.assertEqual(
            mail.outbox[0].body,
            'Hello Bob Munro,\n\nThe quick brown fox.\n\nThank you,\n\n'
            'example.com\n------\nhttp://example.com\n')
        self.assertEqual(
            mail.outbox[0].alternatives[0][0],
            'Hello Bob Munro,<br/><br/><p>The quick brown fox.</p><br/><br/>'
            'Thank you,<br/>example.com<br/>------<br/>http://example.com')

    @patch('small_small_hr.emails.Site.objects.get_current')
    @patch('small_small_hr.emails.render_to_string')
    def test_send_email_templates(self, mock, site_mock):
        """
        Test the templates used with send_email
        """
        mock.return_value = "Some random text"
        site_mock.return_value = 42  # ensure that this is predictable

        # test generic
        data = {
            'name': 'Bob Munro',
            'email': 'bob@example.com',
            'subject': "I love oov",
            'message': "Its dangerous",
        }

        send_email(**data)

        context = data.copy()
        context.pop("email")
        context["object"] = None
        context["SITE"] = 42

        expected_calls = [
            call(
                "small_small_hr/email/generic_email_subject.txt",
                context
            ),
            call(
                "small_small_hr/email/generic_email_body.txt",
                context
            ),
            call(
                "small_small_hr/email/generic_email_body.html",
                context
            )
        ]

        mock.assert_has_calls(expected_calls)

        mock.reset_mock()

        # test leave
        start = datetime(
            2017, 6, 5, 0, 0, 0, tzinfo=pytz.timezone(settings.TIME_ZONE))
        end = datetime(
            2017, 6, 10, 0, 0, 0, tzinfo=pytz.timezone(settings.TIME_ZONE))
        leave = mommy.make(
            'small_small_hr.Leave', staff=self.staffprofile, start=start,
            end=end, leave_type=Leave.SICK,
            status=Leave.PENDING)

        leave_application_email(leave)

        context = dict(
            name="mosh",
            subject="New Leave Application",
            message="There has been a new leave application.  Please log in to process it.",  # noqa
            object=leave,
            SITE=42
        )

        expected_calls = [
            call(
                "small_small_hr/email/leave_application_email_subject.txt",
                context
            ),
            call(
                "small_small_hr/email/leave_application_email_body.txt",
                context
            ),
            call(
                "small_small_hr/email/leave_application_email_body.html",
                context
            )
        ]

        mock.assert_has_calls(expected_calls)

        mock.reset_mock()

        # test overtime
        start = datetime(
            2017, 6, 5, 0, 0, 0, tzinfo=pytz.timezone(settings.TIME_ZONE))
        end = datetime(
            2017, 6, 10, 0, 0, 0, tzinfo=pytz.timezone(settings.TIME_ZONE))
        overtime = mommy.make(
            'small_small_hr.OverTime', staff=self.staffprofile, start=start,
            end=end, status=OverTime.PENDING)

        overtime_application_email(overtime)

        context = dict(
            name="mosh",
            subject="New Overtime Application",
            message="There has been a new overtime application.  Please log in to process it.",  # noqa
            object=overtime,
            SITE=42
        )

        expected_calls = [
            call(
                "small_small_hr/email/overtime_application_email_subject.txt",
                context
            ),
            call(
                "small_small_hr/email/overtime_application_email_body.txt",
                context
            ),
            call(
                "small_small_hr/email/overtime_application_email_body.html",
                context
            )
        ]

        mock.assert_has_calls(expected_calls)
