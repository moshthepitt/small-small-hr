"""
Forms module for small small hr
"""
from django import forms
from django.conf import settings
from django.utils.translation import ugettext as _

from crispy_forms.bootstrap import Field, FormActions
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit
from phonenumber_field.modelfields import PhoneNumberField

from small_small_hr.models import StaffProfile


class StaffProfileAdminForm(forms.ModelForm):
    """
    Form used when managing StaffProfile objects
    """
    first_name = forms.CharField(label=_('First Name'))
    last_name = forms.CharField(label=_('Last Name'))
    id_number = forms.CharField(label=_('ID Number'))
    nhif = forms.CharField(label=_('NHIF'))
    nssf = forms.CharField(label=_('NSSF'))
    pin_number = forms.CharField(label=_('PIN Number'))
    emergency_contact_name = forms.CharField(label=_('Emergecy Contact Name'))
    emergency_contact_number = PhoneNumberField(
        label=_('Emergency Contact Phone Number'))

    class Meta:  # pylint: disable=too-few-public-methods
        """
        Class meta options
        """
        model = StaffProfile
        fields = [
            'user',
            'amount',
            'birthday',
            'sex',
            'leave_days',
            'sick_days',
            'overtime',
            'photo',
            'role',
            'address'
        ]
