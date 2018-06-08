"""
Forms module for small small hr
"""
from django import forms
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
    first_name = forms.CharField(label=_('First Name'), required=True)
    last_name = forms.CharField(label=_('Last Name'), required=True)
    id_number = forms.CharField(label=_('ID Number'), required=True)
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
            'first_name',
            'last_name',
            'id_number',
            'sex',
            'role',
            'nhif',
            'nssf',
            'pin_number',
            'emergency_contact_name',
            'emergency_contact_number',
            'address',
            'birthday',
            'leave_days',
            'sick_days',
            'overtime_allowed',
            'start_date',
            'end_date',
            'emergency_contact_name',
            'emergency_contact_number',
        ]

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = True
        self.helper.form_method = 'post'
        self.helper.render_required_fields = True
        self.helper.form_show_labels = True
        self.helper.html5_required = True
        self.helper.form_id = 'investment-form'
        self.helper.layout = Layout(
            Field('first_name',),
            Field('last_name',),
            Field('id_number',),
            Field('sex',),
            Field('role',),
            Field('nhif',),
            Field('nssf',),
            Field('pin_number',),
            Field('emergency_contact_name',),
            Field('emergency_contact_number',),
            Field('address',),
            Field('birthday',),
            Field('leave_days',),
            Field('sick_days',),
            Field('overtime_allowed',),
            Field('start_date',),
            Field('end_date',),
            Field('emergency_contact_name',),
            Field('emergency_contact_number',),
            FormActions(
                Submit('submitBtn', _('Submit'), css_class='btn-primary'),
            )
        )
