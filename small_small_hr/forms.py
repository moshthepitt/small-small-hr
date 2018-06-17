"""
Forms module for small small hr
"""
from django import forms
from django.utils.translation import ugettext as _

from crispy_forms.bootstrap import Field, FormActions
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit
from phonenumber_field.formfields import PhoneNumberField

from small_small_hr.models import (TWOPLACES, Leave, OverTime, Role,
                                   StaffDocument, StaffProfile)


class RoleForm(forms.ModelForm):
    """
    Form used when managing Role objects
    """

    class Meta:  # pylint: disable=too-few-public-methods
        """
        Class meta options
        """
        model = Role
        fields = [
            'name',
            'description'
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
        self.helper.form_id = 'role-form'
        self.helper.layout = Layout(
            Field('name',),
            Field('description',),
            FormActions(
                Submit('submitBtn', _('Submit'), css_class='btn-primary'),
            )
        )


class OverTimeForm(forms.ModelForm):
    """
    Form used when managing OverTime objects
    """

    class Meta:  # pylint: disable=too-few-public-methods
        """
        Class meta options
        """
        model = OverTime
        fields = [
            'staff',
            'date',
            'start',
            'end',
            'reason',
            'status',
            'comments'
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
        self.helper.form_id = 'overtime-form'
        self.helper.layout = Layout(
            Field('staff',),
            Field('date',),
            Field('start',),
            Field('end',),
            Field('reason',),
            Field('status',),
            Field('comments'),
            FormActions(
                Submit('submitBtn', _('Submit'), css_class='btn-primary'),
            )
        )

    def clean(self):
        """
        Custom clean method
        """
        cleaned_data = super().clean()
        end = cleaned_data.get('end')
        start = cleaned_data.get('start')

        # end must be later than start
        if end <= start:
            self.add_error('end', _("end must be greater than start"))


class ApplyOverTimeForm(OverTimeForm):
    """
    Form used when applying for overtime
    """

    class Meta:  # pylint: disable=too-few-public-methods
        """
        Class meta options
        """
        model = OverTime
        fields = [
            'staff',
            'date',
            'start',
            'end',
            'reason',
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
        self.helper.form_id = 'overtime-application-form'
        self.helper.layout = Layout(
            Field('staff',),
            Field('date',),
            Field('start',),
            Field('end',),
            Field('reason',),
            FormActions(
                Submit('submitBtn', _('Submit'), css_class='btn-primary'),
            )
        )


class LeaveForm(forms.ModelForm):
    """
    Form used when managing Leave objects
    """

    class Meta:  # pylint: disable=too-few-public-methods
        """
        Class meta options
        """
        model = Leave
        fields = [
            'staff',
            'leave_type',
            'start',
            'end',
            'reason',
            'status',
            'comments'
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
        self.helper.form_id = 'leave-form'
        self.helper.layout = Layout(
            Field('staff',),
            Field('leave_type',),
            Field('start',),
            Field('end',),
            Field('reason',),
            Field('status',),
            Field('comments'),
            FormActions(
                Submit('submitBtn', _('Submit'), css_class='btn-primary'),
            )
        )

    def clean(self):
        """
        Custom clean method
        """
        cleaned_data = super().clean()
        leave_type = cleaned_data.get('leave_type')
        staff = cleaned_data.get('staff')
        end = cleaned_data.get('end')
        start = cleaned_data.get('start')

        # end must be later than start
        if end <= start:
            self.add_error('end', _("end must be greater than start"))

        # staff profile must have sufficient sick days
        if leave_type == Leave.SICK:
            sick_days = staff.get_available_sick_days(year=start.year)
            if (end - start).days > sick_days:
                msg = _('Not enough sick days. Available sick days '
                        f'are {sick_days.quantize(TWOPLACES)}')
                self.add_error('start', msg)
                self.add_error('end', msg)

        # staff profile must have sufficient leave days
        if leave_type == Leave.REGULAR:
            leave_days = staff.get_available_leave_days(year=start.year)
            if (end - start).days > leave_days:
                msg = _('Not enough leave days. Available leave days '
                        f'are {leave_days.quantize(TWOPLACES)}')
                self.add_error('start', msg)
                self.add_error('end', msg)


class ApplyLeaveForm(LeaveForm):
    """
    Form used when applying for Leave
    """

    class Meta:  # pylint: disable=too-few-public-methods
        """
        Class meta options
        """
        model = Leave
        fields = [
            'staff',
            'leave_type',
            'start',
            'end',
            'reason',
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
        self.helper.form_id = 'leave-application-form'
        self.helper.layout = Layout(
            Field('staff',),
            Field('leave_type',),
            Field('start',),
            Field('end',),
            Field('reason',),
            FormActions(
                Submit('submitBtn', _('Submit'), css_class='btn-primary'),
            )
        )


class StaffDocumentForm(forms.ModelForm):
    """
    Form used when managing StaffDocument objects
    """

    class Meta:  # pylint: disable=too-few-public-methods
        """
        Class meta options
        """
        model = StaffDocument
        fields = [
            'staff',
            'name',
            'description',
            'file',
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
        self.helper.form_id = 'staffdocument-form'
        self.helper.layout = Layout(
            Field('staff',),
            Field('name',),
            Field('description',),
            Field('file',),
            FormActions(
                Submit('submitBtn', _('Submit'), css_class='btn-primary'),
            )
        )


class StaffProfileAdminForm(forms.ModelForm):
    """
    Form used when managing StaffProfile objects
    """
    first_name = forms.CharField(label=_('First Name'), required=True)
    last_name = forms.CharField(label=_('Last Name'), required=True)
    id_number = forms.CharField(label=_('ID Number'), required=True)
    nhif = forms.CharField(label=_('NHIF'), required=False)
    nssf = forms.CharField(label=_('NSSF'), required=False)
    pin_number = forms.CharField(label=_('PIN Number'), required=False)
    emergency_contact_name = forms.CharField(
        label=_('Emergecy Contact Name'), required=False)
    emergency_contact_number = PhoneNumberField(
        label=_('Emergency Contact Phone Number'), required=False)

    class Meta:  # pylint: disable=too-few-public-methods
        """
        Class meta options
        """
        model = StaffProfile
        fields = [
            'first_name',
            'last_name',
            'id_number',
            'phone',
            'sex',
            'role',
            'nhif',
            'nssf',
            'pin_number',
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
        self.helper.form_id = 'staffprofile-form'
        self.helper.layout = Layout(
            Field('first_name',),
            Field('last_name',),
            Field('phone',),
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

    def clean_id_number(self):
        """
        Check if id number is unique
        """
        value = self.cleaned_data.get('id_number')
        # pylint: disable=no-member
        if StaffProfile.objects.exclude(
                id=self.instance.id).filter(data__id_number=value).exists():
            raise forms.ValidationError(
                _('This id number is already in use.'))
        return value

    def clean_nssf(self):
        """
        Check if NSSF number is unique
        """
        value = self.cleaned_data.get('nssf')
        # pylint: disable=no-member
        if StaffProfile.objects.exclude(
                id=self.instance.id).filter(data__nssf=value).exists():
            raise forms.ValidationError(
                _('This NSSF number is already in use.'))
        return value

    def clean_nhif(self):
        """
        Check if NHIF number is unique
        """
        value = self.cleaned_data.get('nhif')
        # pylint: disable=no-member
        if StaffProfile.objects.exclude(
                id=self.instance.id).filter(data__nhif=value).exists():
            raise forms.ValidationError(
                _('This NHIF number is already in use.'))
        return value

    def clean_pin_number(self):
        """
        Check if PIN number is unique
        """
        value = self.cleaned_data.get('pin_number')
        # pylint: disable=no-member
        if StaffProfile.objects.exclude(
                id=self.instance.id).filter(data__pin_number=value).exists():
            raise forms.ValidationError(
                _('This PIN number is already in use.'))
        return value

    def save(self, commit=True):  # pylint: disable=unused-argument
        """
        Custom save method
        """
        staffprofile = super().save()

        emergency_phone = self.cleaned_data.get('emergency_contact_number')
        emergency_phone = emergency_phone.as_e164

        json_data = {
            'id_number': self.cleaned_data.get('id_number'),
            'nhif': self.cleaned_data.get('nhif'),
            'nssf': self.cleaned_data.get('nssf'),
            'pin_number': self.cleaned_data.get('pin_number'),
            'emergency_contact_name': self.cleaned_data.get(
                'emergency_contact_name'),
            'emergency_contact_number': emergency_phone,
        }
        staffprofile.data = json_data
        staffprofile.save()

        user = staffprofile.user
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.save()
        return staffprofile


class StaffProfileUserForm(StaffProfileAdminForm):
    """
    Form used when the user is updating their own data
    """

    class Meta:  # pylint: disable=too-few-public-methods
        """
        Class meta options
        """
        model = StaffProfile
        fields = [
            'first_name',
            'last_name',
            'id_number',
            'phone',
            'sex',
            'role',
            'nhif',
            'nssf',
            'pin_number',
            'address',
            'birthday',
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
        self.helper.form_id = 'staffprofile-user-form'
        self.helper.layout = Layout(
            Field('first_name',),
            Field('last_name',),
            Field('phone',),
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
            Field('emergency_contact_name',),
            Field('emergency_contact_number',),
            FormActions(
                Submit('submitBtn', _('Submit'), css_class='btn-primary'),
            )
        )