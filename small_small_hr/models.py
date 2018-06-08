"""
Models module for small_small_hr
"""
from django.conf import settings
from django.contrib.postgres.fields import JSONField
from django.db import models
from django.utils.translation import ugettext as _

from phonenumber_field.modelfields import PhoneNumberField
from private_storage.fields import PrivateFileField

USER = settings.AUTH_USER_MODEL


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
    class Meta(object):
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

    class Meta(object):  # pylint: disable=too-few-public-methods
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
    sex = models.CharField(_('Gender'), choices=SEX_CHOICES, max_length=1,
                           default=NOT_KNOWN, blank=True)
    role = models.ForeignKey(Role, verbose_name=_('Role'), blank=True,
                             default=None, null=True,
                             on_delete=models.SET_NULL)
    phone = PhoneNumberField(_('Phone'), blank=True, default='')
    address = models.TextField(_('Addresss'), blank=True, default="")
    birthday = models.DateField(_('Birth day'), blank=True, default=None,
                                null=True)
    leave_days = models.PositiveIntegerField(
        _('Leave days'), default=21, blank=True,
        help_text=_('Number of leave days allowed in a year.'))
    sick_days = models.PositiveIntegerField(
        _('Sick days'), default=21, blank=True,
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

    class Meta(object):  # pylint: disable=too-few-public-methods
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

    def __str__(self):
        return self.get_name()


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
        help_text=_("Upload staff member drocument"),
        content_types=[
            'application/pdf',
            'application/msword',
            'application/vnd.oasis.opendocument.text',
            'image/jpeg',
            'image/png'
        ],
        max_file_size=1048576
    )

    class Meta(object):  # pylint: disable=too-few-public-methods
        """
        Meta options for StaffDocument
        """
        abstract = False
        verbose_name = _('Staff Document')
        verbose_name_plural = _('Staff Documents')
        ordering = ['staff', 'name', 'created']

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
        blank=True)
    comments = models.TextField(_('Comments'), blank=True, default='')

    class Meta(object):  # pylint: disable=too-few-public-methods
        """
        Meta options for StaffDocument
        """
        abstract = True


class Leave(BaseStaffRequest):
    """
    Leave model class
    """

    class Meta(object):  # pylint: disable=too-few-public-methods
        """
        Meta options for Leave
        """
        abstract = False
        verbose_name = _('Leave')
        verbose_name_plural = _('Leave')
        ordering = ['staff', 'start']

    def __str__(self):
        # pylint: disable=no-member
        return _(f'{self.staff.get_name()}: {self.start} to {self.end}')


class OverTime(BaseStaffRequest):
    """
    Overtime model class
    """

    class Meta(object):  # pylint: disable=too-few-public-methods
        """
        Meta options for OverTime
        """
        abstract = False
        verbose_name = _('Overtime')
        verbose_name_plural = _('Overtime')
        ordering = ['staff', 'start']

    def __str__(self):
        # pylint: disable=no-member
        name = self.staff.get_name()
        return _(f'{name}: {self.start.time()} to {self.end.time()}')
