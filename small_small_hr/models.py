"""
Models module for small_small_hr
"""
from datetime import datetime, timedelta
from decimal import Decimal

from django.conf import settings
from django.contrib.postgres.fields import JSONField
from django.db import models
from django.db.models import Q
from django.utils import timezone
from django.utils.translation import ugettext as _

from phonenumber_field.modelfields import PhoneNumberField
from private_storage.fields import PrivateFileField
from sorl.thumbnail import ImageField

from small_small_hr.managers import LeaveManager

USER = settings.AUTH_USER_MODEL
TWOPLACES = Decimal(10) ** -2


class TimeStampedModel(models.Model):
    """
    Abstract model class that includes timestamp fields
    """
    created = models.DateTimeField(
        verbose_name=_('Created'),
        auto_now_add=True)
    modified = models.DateTimeField(
        verbose_name=_('Modified'),
        auto_now=True)

    # pylint: disable=too-few-public-methods
    class Meta:
        """
        Meta options for TimeStampedModel
        """
        abstract = True


class Role(TimeStampedModel, models.Model):
    """
    Model class for staff member role
    """
    name = models.CharField(_('Name'), max_length=255)
    description = models.TextField(_('Description'), blank=True, default='')

    class Meta:  # pylint: disable=too-few-public-methods
        """
        Meta options for StaffDocument
        """
        abstract = False
        verbose_name = _('Role')
        verbose_name_plural = _('Roles')
        ordering = ['name', 'created']

    def __str__(self):
        # pylint: disable=no-member
        return self.name


class StaffProfile(TimeStampedModel, models.Model):
    """
    StaffProfile model class
    Extends auth.User and adds more fields
    """

    # sex choices
    # according to https://en.wikipedia.org/wiki/ISO/IEC_5218
    NOT_KNOWN = '0'
    MALE = '1'
    FEMALE = '2'
    NOT_APPLICABLE = '9'

    SEX_CHOICES = (
        (NOT_KNOWN, _('Not Known')),
        (MALE, _('Male')),
        (FEMALE, _('Female')),
        (NOT_APPLICABLE, _('Not Applicable'))
    )

    user = models.OneToOneField(
        USER, verbose_name=_('User'), on_delete=models.CASCADE)
    image = ImageField(upload_to="staff-images/", max_length=255,
                       verbose_name=_("Profile Image"),
                       help_text=_("A square image works best"), blank=True)
    sex = models.CharField(_('Gender'), choices=SEX_CHOICES, max_length=1,
                           default=NOT_KNOWN, blank=True, db_index=True)
    role = models.ForeignKey(Role, verbose_name=_('Role'), blank=True,
                             default=None, null=True,
                             on_delete=models.SET_NULL)
    phone = PhoneNumberField(_('Phone'), blank=True, default='')
    address = models.TextField(_('Addresss'), blank=True, default="")
    birthday = models.DateField(_('Birthday'), blank=True, default=None,
                                null=True)
    leave_days = models.PositiveIntegerField(
        _('Leave days'), default=21, blank=True,
        help_text=_('Number of leave days allowed in a year.'))
    sick_days = models.PositiveIntegerField(
        _('Sick days'), default=10, blank=True,
        help_text=_('Number of sick days allowed in a year.'))
    overtime_allowed = models.BooleanField(
        _('Overtime allowed'), blank=True, default=False)
    start_date = models.DateField(
        _('Start Date'), null=True, default=None, blank=True,
        help_text=_('The start date of employment'))
    end_date = models.DateField(
        _('End Date'), null=True, default=None, blank=True,
        help_text=_('The end date of employment'))
    data = JSONField(_('Data'), default=dict, blank=True)

    class Meta:  # pylint: disable=too-few-public-methods
        """
        Meta options for StaffProfile
        """
        abstract = False
        verbose_name = _('Staff Profile')
        verbose_name_plural = _('Staff Profiles')
        ordering = ['user__first_name', 'user__last_name', 'user__username',
                    'created']

    def get_name(self):
        """
        Returns the staff member's name
        """
        # pylint: disable=no-member
        return f'{self.user.first_name} {self.user.last_name}'

    def get_approved_leave_days(self, year: int = datetime.today().year):
        """
        Get approved leave days in the current year
        """
        # pylint: disable=no-member
        return get_taken_leave_days(
            staffprofile=self,
            status=Leave.APPROVED,
            leave_type=Leave.REGULAR,
            start_year=year,
            end_year=year
        )

    def get_approved_sick_days(self, year: int = datetime.today().year):
        """
        Get approved leave days in the current year
        """
        return get_taken_leave_days(
            staffprofile=self,
            status=Leave.APPROVED,
            leave_type=Leave.SICK,
            start_year=year,
            end_year=year
        )

    def get_available_leave_days(self, year: int = datetime.today().year):
        """
        Get available leave days
        """
        try:
            # pylint: disable=no-member
            leave_record = AnnualLeave.objects.get(
                leave_type=Leave.REGULAR,
                staff=self,
                year=year)
        except AnnualLeave.DoesNotExist:
            return Decimal(0)
        else:
            return leave_record.get_available_leave_days()

    def get_available_sick_days(self, year: int = datetime.today().year):
        """
        Get available sick days
        """
        try:
            # pylint: disable=no-member
            leave_record = AnnualLeave.objects.get(
                leave_type=Leave.SICK,
                staff=self,
                year=year)
        except AnnualLeave.DoesNotExist:
            return Decimal(0)
        else:
            return leave_record.get_available_leave_days()

    def __str__(self):
        return self.get_name()  # pylint: disable=no-member


class StaffDocument(TimeStampedModel, models.Model):
    """
    StaffDocument model class
    """
    staff = models.ForeignKey(
        StaffProfile, verbose_name=_('Staff Member'), on_delete=models.CASCADE)
    name = models.CharField(_('Name'), max_length=255)
    description = models.TextField(_('Description'), blank=True, default='')
    file = PrivateFileField(
        _('File'), upload_to='staff-documents/',
        help_text=_("Upload staff member document"),
        content_types=[
            'application/pdf',
            'application/msword',
            'application/vnd.oasis.opendocument.text',
            'image/jpeg',
            'image/png'
        ],
        max_file_size=10485760
    )
    public = models.BooleanField(
        _('Public'),
        help_text=_('If public, it will be available to everyone.'),
        blank=True, default=False)

    class Meta:  # pylint: disable=too-few-public-methods
        """
        Meta options for StaffDocument
        """
        abstract = False
        verbose_name = _('Staff Document')
        verbose_name_plural = _('Staff Documents')
        ordering = ['staff', 'name', '-created']

    def __str__(self):
        # pylint: disable=no-member
        return f'{self.staff.get_name()} - {self.name}'


class BaseStaffRequest(TimeStampedModel, models.Model):
    """
    Abstract model class for Leave & Overtime tracking
    """
    APPROVED = '1'
    REJECTED = '2'
    PENDING = '3'

    STATUS_CHOICES = (
        (APPROVED, _('Approved')),
        (PENDING, _('Pending')),
        (REJECTED, _('Rejected'))
    )

    staff = models.ForeignKey(
        StaffProfile, verbose_name=_('Staff Member'), on_delete=models.CASCADE)
    start = models.DateTimeField(_('Start Date'))
    end = models.DateTimeField(_('End Date'))
    reason = models.TextField(_('Reason'), blank=True, default='')
    status = models.CharField(
        _('Status'), max_length=1, choices=STATUS_CHOICES, default=PENDING,
        blank=True, db_index=True)
    comments = models.TextField(_('Comments'), blank=True, default='')

    class Meta:  # pylint: disable=too-few-public-methods
        """
        Meta options for StaffDocument
        """
        abstract = True


class Leave(BaseStaffRequest):
    """
    Leave model class
    """
    SICK = '1'
    REGULAR = '2'

    TYPE_CHOICES = (
        (SICK, _('Sick Leave')),
        (REGULAR, _('Regular Leave')),
    )

    leave_type = models.CharField(
        _('Type'), max_length=1, choices=TYPE_CHOICES, default=REGULAR,
        blank=True, db_index=True)

    objects = LeaveManager()

    class Meta:  # pylint: disable=too-few-public-methods
        """
        Meta options for Leave
        """
        abstract = False
        verbose_name = _('Leave')
        verbose_name_plural = _('Leave')
        ordering = ['staff', '-start']

    def __str__(self):
        # pylint: disable=no-member
        return _(f'{self.staff.get_name()}: {self.start} to {self.end}')


class OverTime(BaseStaffRequest):
    """
    Overtime model class
    """
    date = models.DateField(
        _('Date'), auto_now=False, auto_now_add=False, db_index=True)
    start = models.TimeField(_('Start'), auto_now=False, auto_now_add=False)
    end = models.TimeField(_('End'), auto_now=False, auto_now_add=False)

    class Meta:  # pylint: disable=too-few-public-methods
        """
        Meta options for OverTime
        """
        abstract = False
        verbose_name = _('Overtime')
        verbose_name_plural = _('Overtime')
        ordering = ['staff', '-date', 'start']

    def __str__(self):
        name = self.staff.get_name()  # pylint: disable=no-member
        return _(f'{name}: {self.date} from {self.start} to {self.end}')

    def get_duration(self):
        """
        Get duration
        """
        start = datetime.combine(self.date, self.start)
        end = datetime.combine(self.date, self.end)
        return end - start


class AnnualLeave(TimeStampedModel, models.Model):
    """
    Model to keep track of staff employee annual leave

    This model is meant to be populated once a year
    Each staff member can only have one record per leave_type per year
    """
    YEAR_CHOICES = [
        (r, r) for r in range(2017, datetime.today().year + 10)
    ]

    year = models.PositiveIntegerField(
        _('Year'), choices=YEAR_CHOICES, default=2017, db_index=True)
    staff = models.ForeignKey(
        StaffProfile, verbose_name=_('Staff Member'), on_delete=models.CASCADE)
    leave_type = models.CharField(
        _('Type'), max_length=1, choices=Leave.TYPE_CHOICES, db_index=True)
    allowed_days = models.PositiveIntegerField(
        _('Allowed Leave days'), default=21, blank=True,
        help_text=_('Number of leave days allowed in a year.'))
    carried_over_days = models.PositiveIntegerField(
        _('Carried Over Leave days'), default=0, blank=True,
        help_text=_('Number of leave days carried over into this year.'))

    class Meta:  # pylint: disable=too-few-public-methods
        """
        Meta options for AnnualLeave
        """
        verbose_name = _('Annual Leave')
        verbose_name_plural = _('Annual Leave')
        ordering = ['-year', 'leave_type', 'staff']
        unique_together = (('year', 'staff', 'leave_type'),)

    def __str__(self):
        # pylint: disable=no-member
        return _(
            f'{self.year}: {self.staff.get_name()} '
            f'{self.get_leave_type_display()}')

    def get_cumulative_leave_taken(self):
        """
        Get the cumulative leave taken

        Returns a timedelta
        """
        return get_taken_leave_days(
            staffprofile=self.staff,
            status=Leave.APPROVED,
            leave_type=self.leave_type,
            start_year=self.year,
            end_year=self.year
        )

    def get_available_leave_days(self, month: int = 12):
        """
        Get the remaining leave days
        """
        if month <= 0:
            month = 1
        elif month > 12:
            month = 12

        # the max allowed days per year
        allowed = self.allowed_days

        # the days `earned` per month
        per_month = Decimal(allowed / 12)

        # the days earned so far, given the month
        earned = Decimal(month) * per_month

        # the days taken
        taken = self.get_cumulative_leave_taken()

        # the starting balance
        starting_balance = self.carried_over_days

        return Decimal(earned + starting_balance - taken)


class FreeDay(models.Model):
    """Model definition for FreeDay."""
    name = models.CharField(_("Name"), max_length=255)
    date = models.DateField(_('Date'), unique=True)

    class Meta:
        """Meta definition for FreeDay."""
        ordering = ['-date']
        verbose_name = _('Free Day')
        verbose_name_plural = _('Free Days')

    def __str__(self):
        """Unicode representation of FreeDay."""
        return f"{self.date.year} - {self.name}"


def get_days(start: object, end: object):
    """
    Yield the days between two datetime objects
    """
    current_tz = timezone.get_current_timezone()
    local_start = current_tz.normalize(start)
    local_end = current_tz.normalize(end)
    span = local_end.date() - local_start.date()
    for i in range(span.days + 1):
        yield local_start.date() + timedelta(days=i)


def get_taken_leave_days(
        staffprofile: object,
        status: str,
        leave_type: str,
        start_year: int,
        end_year: int):
    """
    Calculate the number of leave days actually taken,
    taking into account weekends and weekend policy
    """
    count = Decimal(0)
    free_days = FreeDay.objects.filter(
        date__year__gte=start_year, date__year__lte=end_year
    ).values_list('date', flat=True)
    queryset = Leave.objects.filter(
        staff=staffprofile,
        status=status,
        leave_type=leave_type).filter(
            Q(start__year__gte=start_year) | Q(end__year__lte=end_year))
    for leave_obj in queryset:
        days = get_days(start=leave_obj.start, end=leave_obj.end)
        for day in days:
            if day.year >= start_year and day.year <= end_year and\
                    day not in free_days:
                day_value = settings.SSHR_DAY_LEAVE_VALUES[day.isoweekday()]
                count = count + Decimal(day_value)
    return count
