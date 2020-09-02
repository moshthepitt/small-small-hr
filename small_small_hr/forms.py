"""Forms module for small small hr."""
from datetime import datetime, time

from django import forms
from django.conf import settings
from django.contrib.auth.models import User  # pylint: disable = imported-auth-user
from django.db.models import Q
from django.utils.translation import ugettext as _

import pytz
from crispy_forms.bootstrap import Field, FormActions
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit
from phonenumber_field.formfields import PhoneNumberField
from phonenumber_field.phonenumber import PhoneNumber

from small_small_hr.models import (
    TWOPLACES,
    AnnualLeave,
    FreeDay,
    Leave,
    OverTime,
    Role,
    StaffDocument,
    StaffProfile,
)


class AnnualLeaveForm(forms.ModelForm):
    """Form used when managing AnnualLeave."""

    class Meta:  # pylint: disable=too-few-public-methods
        """Class meta options."""

        model = AnnualLeave
        fields = ["staff", "year", "leave_type", "allowed_days", "carried_over_days"]

    def __init__(self, *args, **kwargs):
        """Initialize the form."""
        self.request = kwargs.pop("request", None)
        super().__init__(*args, **kwargs)
        if not self.instance:
            self.fields["year"].initial = datetime.today().year
        self.helper = FormHelper()
        self.helper.form_tag = True
        self.helper.form_method = "post"
        self.helper.render_required_fields = True
        self.helper.form_show_labels = True
        self.helper.html5_required = True
        self.helper.form_id = "annual-leave-form"
        self.helper.layout = Layout(
            Field("staff",),
            Field("year",),
            Field("leave_type",),
            Field("allowed_days",),
            Field("carried_over_days"),
            FormActions(Submit("submitBtn", _("Submit"), css_class="btn-primary"),),
        )


class RoleForm(forms.ModelForm):
    """Form used when managing Role objects."""

    class Meta:  # pylint: disable=too-few-public-methods
        """Class meta options."""

        model = Role
        fields = ["name", "description"]

    def __init__(self, *args, **kwargs):
        """Initialize the form."""
        self.request = kwargs.pop("request", None)
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = True
        self.helper.form_method = "post"
        self.helper.render_required_fields = True
        self.helper.form_show_labels = True
        self.helper.html5_required = True
        self.helper.form_id = "role-form"
        self.helper.layout = Layout(
            Field("name",),
            Field("description",),
            FormActions(Submit("submitBtn", _("Submit"), css_class="btn-primary"),),
        )


class FreeDayForm(forms.ModelForm):
    """Form used when managing FreeDay objects."""

    class Meta:  # pylint: disable=too-few-public-methods
        """Class meta options."""

        model = FreeDay
        fields = ["name", "date"]

    def __init__(self, *args, **kwargs):
        """Initialize the form."""
        self.request = kwargs.pop("request", None)
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = True
        self.helper.form_method = "post"
        self.helper.render_required_fields = True
        self.helper.form_show_labels = True
        self.helper.html5_required = True
        self.helper.form_id = "freeday-form"
        self.helper.layout = Layout(
            Field("name",),
            Field("date",),
            FormActions(Submit("submitBtn", _("Submit"), css_class="btn-primary"),),
        )


class OverTimeForm(forms.ModelForm):
    """Form used when managing OverTime objects."""

    class Meta:  # pylint: disable=too-few-public-methods
        """Class meta options."""

        model = OverTime
        fields = [
            "staff",
            "date",
            "start",
            "end",
            "review_reason",
            "review_status",
        ]

    def __init__(self, *args, **kwargs):
        """Initialize the form."""
        self.request = kwargs.pop("request", None)
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = True
        self.helper.form_method = "post"
        self.helper.render_required_fields = True
        self.helper.form_show_labels = True
        self.helper.html5_required = True
        self.helper.form_id = "overtime-form"
        self.helper.layout = Layout(
            Field("staff",),
            Field("date",),
            Field("start",),
            Field("end",),
            Field("review_reason",),
            Field("review_status",),
            FormActions(Submit("submitBtn", _("Submit"), css_class="btn-primary"),),
        )

    def clean(self):
        """Clean all the form fields."""
        cleaned_data = super().clean()
        end = cleaned_data.get("end")
        start = cleaned_data.get("start")
        date = cleaned_data.get("date")
        staff = cleaned_data.get("staff")
        review_status = cleaned_data.get("review_status")

        # end must be later than start
        if end <= start:
            self.add_error("end", _("end must be greater than start"))

        # must not overlap within the same date unless being rejected
        # pylint: disable=no-member
        overlap_qs = OverTime.objects.filter(
            date=date, staff=staff, review_status=OverTime.APPROVED
        ).filter(Q(start__gte=start) & Q(end__lte=end))

        if self.instance is not None:
            overlap_qs = overlap_qs.exclude(id=self.instance.id)

        if overlap_qs.exists() and review_status != OverTime.REJECTED:
            msg = _("you cannot have overlapping overtime hours on the " "same day")
            self.add_error("start", msg)
            self.add_error("end", msg)
            self.add_error("date", msg)


class ApplyOverTimeForm(OverTimeForm):
    """Form used when applying for overtime."""

    class Meta:  # pylint: disable=too-few-public-methods
        """Class meta options."""

        model = OverTime
        fields = [
            "staff",
            "date",
            "start",
            "end",
            "review_reason",
        ]

    def __init__(self, *args, **kwargs):
        """Initialize the form."""
        super().__init__(*args, **kwargs)
        self.request = kwargs.pop("request", None)
        if self.request:
            # pylint: disable=no-member
            try:
                self.request.user.staffprofile
            except StaffProfile.DoesNotExist:
                pass
            else:
                self.fields["staff"].queryset = StaffProfile.objects.filter(
                    id=self.request.user.staffprofile.id
                )
        self.helper = FormHelper()
        self.helper.form_tag = True
        self.helper.form_method = "post"
        self.helper.render_required_fields = True
        self.helper.form_show_labels = True
        self.helper.html5_required = True
        self.helper.form_id = "overtime-application-form"
        self.helper.layout = Layout(
            Field("staff", type="hidden"),
            Field("date",),
            Field("start",),
            Field("end",),
            Field("review_reason",),
            FormActions(Submit("submitBtn", _("Submit"), css_class="btn-primary"),),
        )

    def save(self, commit=True):
        """Save the form."""
        overtime = super().save()
        return overtime


class LeaveForm(forms.ModelForm):
    """Form used when managing Leave objects."""

    start = forms.DateField(label=_("Start Date"), required=True)
    end = forms.DateField(label=_("End Date"), required=True)

    class Meta:  # pylint: disable=too-few-public-methods
        """Class meta options."""

        model = Leave
        fields = [
            "staff",
            "leave_type",
            "start",
            "end",
            "review_reason",
            "review_status",
        ]

    def __init__(self, *args, **kwargs):
        """Initialize the form."""
        self.request = kwargs.pop("request", None)
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = True
        self.helper.form_method = "post"
        self.helper.render_required_fields = True
        self.helper.form_show_labels = True
        self.helper.html5_required = True
        self.helper.form_id = "leave-form"
        self.helper.layout = Layout(
            Field("staff",),
            Field("leave_type",),
            Field("start",),
            Field("end",),
            Field("review_reason",),
            Field("review_status",),
            FormActions(Submit("submitBtn", _("Submit"), css_class="btn-primary"),),
        )

    def clean_start(self):
        """Clean start field."""
        data = self.cleaned_data["start"]
        data = datetime.combine(
            date=data,
            time=time(settings.SSHR_DEFAULT_TIME, 0, 0, 0),
            tzinfo=pytz.timezone(settings.TIME_ZONE),
        )
        return data

    def clean_end(self):
        """Clean end field."""
        data = self.cleaned_data["end"]
        data = datetime.combine(
            date=data,
            time=time(settings.SSHR_DEFAULT_TIME, 0, 0, 0),
            tzinfo=pytz.timezone(settings.TIME_ZONE),
        )
        return data

    def clean(self):
        """Clean all the form fields."""
        cleaned_data = super().clean()
        leave_type = cleaned_data.get("leave_type")
        staff = cleaned_data.get("staff")
        end = cleaned_data.get("end")
        start = cleaned_data.get("start")
        review_status = cleaned_data.get("review_status")

        if all([staff, leave_type, start, end]):
            # end year and start year must be the same
            if end.year != start.year:
                msg = _("start and end must be from the same year")
                self.add_error("start", msg)
                self.add_error("end", msg)

            # end must be later than start
            if end < start:
                self.add_error("end", _("end must be greater than start"))

            if not settings.SSHR_ALLOW_OVERSUBSCRIBE:
                # staff profile must have sufficient sick days
                if leave_type == Leave.SICK:
                    sick_days = staff.get_available_sick_days(year=start.year)
                    if (end - start).days > sick_days:
                        msg = _(
                            "Not enough sick days. Available sick days "
                            f"are {sick_days.quantize(TWOPLACES)}"
                        )
                        self.add_error("start", msg)
                        self.add_error("end", msg)

                # staff profile must have sufficient leave days
                if leave_type == Leave.REGULAR:
                    leave_days = staff.get_available_leave_days(year=start.year)
                    if (end - start).days > leave_days:
                        msg = _(
                            "Not enough leave days. Available leave days "
                            f"are {leave_days.quantize(TWOPLACES)}"
                        )
                        self.add_error("start", msg)
                        self.add_error("end", msg)

            # must not overlap unless it is being rejected
            # pylint: disable=no-member
            overlap_qs = Leave.objects.filter(
                staff=staff, review_status=Leave.APPROVED, leave_type=leave_type
            ).filter(Q(start__gte=start) & Q(end__lte=end))

            if self.instance is not None:
                overlap_qs = overlap_qs.exclude(id=self.instance.id)

            if overlap_qs.exists() and review_status != Leave.REJECTED:
                msg = _("you cannot have overlapping leave days")
                self.add_error("start", msg)
                self.add_error("end", msg)


class ApplyLeaveForm(LeaveForm):
    """Form used when applying for Leave."""

    class Meta:  # pylint: disable=too-few-public-methods
        """Class meta options."""

        model = Leave
        fields = [
            "staff",
            "leave_type",
            "start",
            "end",
            "review_reason",
        ]

    def __init__(self, *args, **kwargs):
        """Initialize the form."""
        super().__init__(*args, **kwargs)
        self.request = kwargs.pop("request", None)
        if self.request:
            # pylint: disable=no-member
            try:
                self.request.user.staffprofile
            except StaffProfile.DoesNotExist:
                pass
            else:
                self.fields["staff"].queryset = StaffProfile.objects.filter(
                    id=self.request.user.staffprofile.id
                )
        self.helper = FormHelper()
        self.helper.form_tag = True
        self.helper.form_method = "post"
        self.helper.render_required_fields = True
        self.helper.form_show_labels = True
        self.helper.html5_required = True
        self.helper.form_id = "leave-application-form"
        self.helper.layout = Layout(
            Field("staff", type="hidden"),
            Field("leave_type",),
            Field("start",),
            Field("end",),
            Field("review_reason",),
            FormActions(Submit("submitBtn", _("Submit"), css_class="btn-primary"),),
        )

    def save(self, commit=True):
        """Save the form."""
        leave = super().save()
        return leave


class StaffDocumentForm(forms.ModelForm):
    """Form used when managing StaffDocument objects."""

    class Meta:  # pylint: disable=too-few-public-methods
        """Class meta options."""

        model = StaffDocument
        fields = [
            "staff",
            "name",
            "description",
            "public",
            "file",
        ]

    def __init__(self, *args, **kwargs):
        """Initialize the form."""
        self.request = kwargs.pop("request", None)
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.file:
            self.fields["file"].required = False
        self.helper = FormHelper()
        self.helper.form_tag = True
        self.helper.form_method = "post"
        self.helper.render_required_fields = True
        self.helper.form_show_labels = True
        self.helper.html5_required = True
        self.helper.form_id = "staffdocument-form"
        self.helper.layout = Layout(
            Field("staff",),
            Field("name",),
            Field("description",),
            Field("file",),
            Field("public",),
            FormActions(Submit("submitBtn", _("Submit"), css_class="btn-primary"),),
        )


class UserStaffDocumentForm(forms.ModelForm):
    """Form used when managing one's own StaffDocument objects."""

    class Meta:  # pylint: disable=too-few-public-methods
        """Class meta options."""

        model = StaffDocument
        fields = [
            "staff",
            "name",
            "description",
            "file",
        ]

    def __init__(self, *args, **kwargs):
        """Initialize the form."""
        self.request = kwargs.pop("request", None)
        super().__init__(*args, **kwargs)
        if self.request:
            # pylint: disable=no-member
            try:
                self.request.user.staffprofile
            except StaffProfile.DoesNotExist:
                pass
            else:
                self.fields["staff"].queryset = StaffProfile.objects.filter(
                    id=self.request.user.staffprofile.id
                )
        if self.instance and self.instance.file:
            self.fields["file"].required = False
        self.helper = FormHelper()
        self.helper.form_tag = True
        self.helper.form_method = "post"
        self.helper.render_required_fields = True
        self.helper.form_show_labels = True
        self.helper.html5_required = True
        self.helper.form_id = "staffdocument-form"
        self.helper.layout = Layout(
            Field("staff", type="hidden"),
            Field("name",),
            Field("description",),
            Field("file",),
            FormActions(Submit("submitBtn", _("Submit"), css_class="btn-primary"),),
        )


class StaffProfileAdminForm(forms.ModelForm):
    """Form used when managing StaffProfile objects."""

    first_name = forms.CharField(label=_("First Name"), required=True)
    last_name = forms.CharField(label=_("Last Name"), required=True)
    id_number = forms.CharField(label=_("ID Number"), required=True)
    nhif = forms.CharField(label=_("NHIF"), required=False)
    nssf = forms.CharField(label=_("NSSF"), required=False)
    pin_number = forms.CharField(label=_("PIN Number"), required=False)
    emergency_contact_name = forms.CharField(
        label=_("Emergency Contact Name"), required=False
    )
    emergency_contact_relationship = forms.CharField(
        label=_("Emergency Contact Relationship"), required=False
    )
    emergency_contact_number = PhoneNumberField(
        label=_("Emergency Contact Phone Number"), required=False
    )

    class Meta:  # pylint: disable=too-few-public-methods
        """Class meta options."""

        model = StaffProfile
        fields = [
            "first_name",
            "last_name",
            "id_number",
            "image",
            "phone",
            "sex",
            "role",
            "nhif",
            "nssf",
            "pin_number",
            "address",
            "birthday",
            "leave_days",
            "sick_days",
            "overtime_allowed",
            "start_date",
            "end_date",
            "emergency_contact_name",
            "emergency_contact_number",
            "emergency_contact_relationship",
            "supervisor",
        ]

    def __init__(self, *args, **kwargs):
        """Initialize the form."""
        self.request = kwargs.pop("request", None)
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.image:
            self.fields["image"].required = False
        self.helper = FormHelper()
        self.helper.form_tag = True
        self.helper.form_method = "post"
        self.helper.render_required_fields = True
        self.helper.form_show_labels = True
        self.helper.html5_required = True
        self.helper.form_id = "staffprofile-form"
        self.helper.layout = Layout(
            Field("first_name",),
            Field("last_name",),
            Field("supervisor",),
            Field("image",),
            Field("phone",),
            Field("id_number",),
            Field("sex",),
            Field("role",),
            Field("nhif",),
            Field("nssf",),
            Field("pin_number",),
            Field("address",),
            Field("birthday",),
            Field("leave_days",),
            Field("sick_days",),
            Field("overtime_allowed",),
            Field("start_date",),
            Field("end_date",),
            Field("emergency_contact_name",),
            Field("emergency_contact_number",),
            Field("emergency_contact_relationship",),
            FormActions(Submit("submitBtn", _("Submit"), css_class="btn-primary"),),
        )

    def clean_id_number(self):
        """Check if id number is unique."""
        value = self.cleaned_data.get("id_number")
        # pylint: disable=no-member
        if (
            StaffProfile.objects.exclude(id=self.instance.id)
            .filter(data__id_number=value)
            .exists()
        ):
            raise forms.ValidationError(_("This id number is already in use."))
        return value

    def clean_nssf(self):
        """Check if NSSF number is unique."""
        value = self.cleaned_data.get("nssf")
        # pylint: disable=no-member
        if (
            value
            and StaffProfile.objects.exclude(id=self.instance.id)
            .filter(data__nssf=value)
            .exists()
        ):
            raise forms.ValidationError(_("This NSSF number is already in use."))
        return value

    def clean_nhif(self):
        """Check if NHIF number is unique."""
        value = self.cleaned_data.get("nhif")
        # pylint: disable=no-member
        if (
            value
            and StaffProfile.objects.exclude(id=self.instance.id)
            .filter(data__nhif=value)
            .exists()
        ):
            raise forms.ValidationError(_("This NHIF number is already in use."))
        return value

    def clean_pin_number(self):
        """Check if PIN number is unique."""
        value = self.cleaned_data.get("pin_number")
        # pylint: disable=no-member
        if (
            value
            and StaffProfile.objects.exclude(id=self.instance.id)
            .filter(data__pin_number=value)
            .exists()
        ):
            raise forms.ValidationError(_("This PIN number is already in use."))
        return value

    def save(self, commit=True):  # pylint: disable=unused-argument
        """Save the form."""
        staffprofile = super().save()

        emergency_phone = self.cleaned_data.get("emergency_contact_number")
        if isinstance(emergency_phone, PhoneNumber):
            emergency_phone = emergency_phone.as_e164

        json_data = {
            "id_number": self.cleaned_data.get("id_number"),
            "nhif": self.cleaned_data.get("nhif"),
            "nssf": self.cleaned_data.get("nssf"),
            "pin_number": self.cleaned_data.get("pin_number"),
            "emergency_contact_name": self.cleaned_data.get("emergency_contact_name"),
            "emergency_contact_relationship": self.cleaned_data.get(
                "emergency_contact_relationship"
            ),
            "emergency_contact_number": emergency_phone,
        }
        staffprofile.data = json_data
        staffprofile.save()

        user = staffprofile.user
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]
        user.save()
        return staffprofile


class StaffProfileAdminCreateForm(StaffProfileAdminForm):
    """Form used when creating new Staff Profiles."""

    user = forms.ModelChoiceField(
        label=_("User"), queryset=User.objects.filter(staffprofile=None)
    )

    class Meta:  # pylint: disable=too-few-public-methods
        """Class meta options."""

        model = StaffProfile
        fields = [
            "user",
            "first_name",
            "last_name",
            "supervisor",
            "id_number",
            "image",
            "phone",
            "sex",
            "role",
            "nhif",
            "nssf",
            "pin_number",
            "address",
            "birthday",
            "leave_days",
            "sick_days",
            "overtime_allowed",
            "start_date",
            "end_date",
            "emergency_contact_name",
            "emergency_contact_number",
            "emergency_contact_relationship",
        ]

    def __init__(self, *args, **kwargs):
        """Initialize the form."""
        self.request = kwargs.pop("request", None)
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.image:
            self.fields["image"].required = False
        self.helper = FormHelper()
        self.helper.form_tag = True
        self.helper.form_method = "post"
        self.helper.render_required_fields = True
        self.helper.form_show_labels = True
        self.helper.html5_required = True
        self.helper.form_id = "staffprofile-form"
        self.helper.layout = Layout(
            Field("user",),
            Field("first_name",),
            Field("last_name",),
            Field("supervisor",),
            Field("image",),
            Field("phone",),
            Field("id_number",),
            Field("sex",),
            Field("role",),
            Field("nhif",),
            Field("nssf",),
            Field("pin_number",),
            Field("address",),
            Field("birthday",),
            Field("leave_days",),
            Field("sick_days",),
            Field("overtime_allowed",),
            Field("start_date",),
            Field("end_date",),
            Field("emergency_contact_name",),
            Field("emergency_contact_number",),
            Field("emergency_contact_relationship",),
            FormActions(Submit("submitBtn", _("Submit"), css_class="btn-primary"),),
        )


class StaffProfileUserForm(StaffProfileAdminForm):
    """Form used when the user is updating their own data."""

    class Meta:  # pylint: disable=too-few-public-methods
        """Class meta options."""

        model = StaffProfile
        fields = [
            "first_name",
            "last_name",
            "id_number",
            "image",
            "phone",
            "sex",
            "nhif",
            "nssf",
            "pin_number",
            "address",
            "birthday",
            "emergency_contact_name",
            "emergency_contact_number",
            "emergency_contact_relationship",
        ]

    def __init__(self, *args, **kwargs):
        """Initialize the form."""
        self.request = kwargs.pop("request", None)
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = True
        self.helper.form_method = "post"
        self.helper.render_required_fields = True
        self.helper.form_show_labels = True
        self.helper.html5_required = True
        self.helper.form_id = "staffprofile-user-form"
        self.helper.layout = Layout(
            Field("first_name",),
            Field("last_name",),
            Field("image",),
            Field("phone",),
            Field("id_number",),
            Field("sex",),
            Field("nhif",),
            Field("nssf",),
            Field("pin_number",),
            Field("address",),
            Field("birthday",),
            Field("emergency_contact_name",),
            Field("emergency_contact_number",),
            Field("emergency_contact_relationship",),
            FormActions(Submit("submitBtn", _("Submit"), css_class="btn-primary"),),
        )
